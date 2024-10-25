from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import time
from live.report_utils.get_recording import get_recording, NoRecordingsFound, ReportAlreadyExists
from live.models import User, Reports
from live.report_utils.vtt_preprocess import vtt_preprocess, PatientNotFound
from live.report_utils.preprocess_audio import get_mfccs
from live.report_utils.generate_transcript import generate_transcript
from live.report_utils.video_process import video_process
from live.report_utils.gpt_inference import gpt_inference
from live.report_utils.infer import infer
from live.report_utils.gpt_summary import gpt_summary
from live.report_utils.generate_report import generate_report_util
from django.http import HttpResponse
import live.report_utils.garbage_collect as gcc
from typing import Tuple, Dict, Any
from django.http import HttpRequest, HttpResponse

@api_view(["POST"])
def generate_report(request: HttpRequest) -> Response:
    """
    Generates the patient report for the most recent Zoom clinical interview based on the provided therapist ID.

    Args:
        request (HttpRequest): The HTTP request object containing the therapist ID.

    Returns:
        Response: A JSON response indicating the number of reports generated.
    """

    json_data = json.loads(request.body)  # Extract the therapist ID from the request body
    therapist_id = json_data["therapist_id"]

    # Get the user refresh token
    user = User.objects.get(id=therapist_id)
    refresh_code = user.refresh_token

    # Get the recording from Zoom
    try:
        temp_mp4, temp_vtt, report_id, date = get_recording(therapist_id, refresh_code)
    except ReportAlreadyExists:
        print("Error, report for this meeting already exists.")
        return Response({"num_generated": 0})
    except NoRecordingsFound:
        print("Error, no recordings found.")
        return Response({"num_generated": 0})

    # Preprocess the VTT file
    try:
        vtt_data, patient_name = vtt_preprocess(therapist_id, temp_vtt)
    except PatientNotFound:
        return HttpResponse("Patient not found", status=404)

    # Preprocess the audio file
    mfccs, temp_wav = get_mfccs(temp_mp4, vtt_data, report_id)

    # Generate the transcript from the VTT data
    full_transcript = generate_transcript(vtt_data)

    # Process the video file
    aus, mfccs, temp_avi, temp_frames_dir, temp_output_dir = video_process(temp_mp4, vtt_data, mfccs)

    # Perform GPT inference on the transcript
    gpt_output = gpt_inference(full_transcript)

    # Run inference on the AUs, MFCCs, and GPT output
    final_diagnosis_binary = infer(aus, mfccs, gpt_output)

    # Generate a summary from the transcript and diagnosis
    summary = gpt_summary(full_transcript, final_diagnosis_binary)

    # Get the current date in mm/dd/yyyy format
    date = time.strftime("%m/%d/%Y")

    # Generate the report object
    report_object = generate_report_util(final_diagnosis_binary, gpt_output, date, summary, patient_name)

    # Save the report to a temporary HTML file
    report_object.save(path=f'report_{report_id}.html', open=False)

    # Get the path to the temporary report file
    temp_report_path = f'report_{report_id}.html'

    # Read the HTML data from the temporary report file
    with open(temp_report_path, "r") as file:
        html_data = file.read()

    # Create a new report object in the database
    report = Reports(
        id=report_id,
        user=user,
        patient_name=patient_name,
        report=str(html_data),
        url=f"/report/{report_id}",
        date=date
    )

    # Save the report to the database
    report.save()

    # Delete temporary files
    gcc.delete_temp()
    gcc.collect_garbages_file(temp_report_path, rel=False)

    return Response({"num_generated": 1})