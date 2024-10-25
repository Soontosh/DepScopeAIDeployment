""" TAKES IN THERAPIST NAME, VTT_PATH; RETURNS VTT_DATA"""
from typing import Dict, Tuple, List, Any
from live.models import User

# Custom error class, PatientNotFound
class PatientNotFound(Exception):
    pass

def parse_vtt_line(line: str) -> Tuple[float, float, str, str]:
    """
    Parses a line from the VTT file to extract start time, end time, speaker, and text.

    Args:
        line (str): A line from the VTT file.

    Returns:
        Tuple[float, float, str, str]: The start time, end time, speaker, and text.
    """
    start_time, end_time = line.split(" --> ")
    start_time = sum(x * float(t) for x, t in zip([3600, 60, 1], start_time.split(":")))
    end_time = sum(x * float(t) for x, t in zip([3600, 60, 1], end_time.split(":")))
    return start_time, end_time

def extract_vtt_data(lines: List[str]) -> Dict[int, Dict[str, Any]]:
    """
    Extracts VTT data from the lines of the VTT file.

    Args:
        lines (List[str]): The lines of the VTT file.

    Returns:
        Dict[int, Dict[str, Any]]: The extracted VTT data.
    """
    vtt_data = {}
    for i, line in enumerate(lines):
        if line.isdigit():
            start_time, end_time = parse_vtt_line(lines[i + 1])
            text = lines[i + 2]
            speaker = text.split(":")[0]
            text = text.replace(speaker + ": ", "")
            vtt_data[int(line)] = {
                "speaker": speaker,
                "start_time": start_time,
                "end_time": end_time,
                "text": text
            }
    return vtt_data

def replace_speakers(vtt_data: Dict[int, Dict[str, Any]], therapist_name: str) -> str:
    """
    Replaces the speaker names in the VTT data with "Therapist" and "Patient".

    Args:
        vtt_data (Dict[int, Dict[str, Any]]): The VTT data.
        therapist_name (str): The name of the therapist.

    Returns:
        str: The name of the patient.
    """
    patient_name = None
    for key in vtt_data:
        if vtt_data[key]["speaker"] == therapist_name:
            vtt_data[key]["speaker"] = "Therapist"
        else:
            patient_name = vtt_data[key]["speaker"]
            vtt_data[key]["speaker"] = "Patient"
    return patient_name

def vtt_preprocess(therapist_id: str, vtt_path: str) -> Tuple[Dict[int, Dict[str, Any]], str]:
    """
    Preprocesses the VTT file to extract and format the VTT data.

    Args:
        therapist_id (str): The ID of the therapist.
        vtt_path (str): The path to the VTT file.

    Returns:
        Tuple[Dict[int, Dict[str, Any]], str]: The formatted VTT data and the patient name.

    Raises:
        PatientNotFound: If the patient name is not found in the VTT data.
    """
    # Load the VTT file
    with open(vtt_path, "r") as f:
        vtt = f.read()

    # Split the VTT file into lines
    lines = vtt.split("\n")

    # Extract VTT data from the lines
    vtt_data = extract_vtt_data(lines)

    # Find the therapist name
    therapist = User.objects.get(id=therapist_id)
    therapist_name = f"{therapist.first_name} {therapist.last_name}"

    # Replace speaker names in the VTT data
    patient_name = replace_speakers(vtt_data, therapist_name)

    # DEBUG ONLY: Manually set some speaker names to "Patient"
    debug_patient_speakers(vtt_data)

    # If patient name is None, raise PatientNotFound
    if patient_name is None:
        raise PatientNotFound("Patient not found in the transcript")

    return vtt_data, patient_name

def debug_patient_speakers(vtt_data: Dict[int, Dict[str, Any]]) -> None:
    """
    DEBUG ONLY: Manually sets some speaker names to "Patient" for testing purposes.

    Args:
        vtt_data (Dict[int, Dict[str, Any]]): The VTT data.
    """
    debug_indices = [3, 4, 6, 7, 10, 11]
    for index in debug_indices:
        if index in vtt_data:
            vtt_data[index]["speaker"] = "Patient"
    vtt_data[3]["speaker"] = "Patient"
    vtt_data[4]["speaker"] = "Patient"
    vtt_data[6]["speaker"] = "Patient"
    vtt_data[7]["speaker"] = "Patient"
    vtt_data[10]["speaker"] = "Patient"
    vtt_data[11]["speaker"] = "Patient"
    patient_name = "Janny Wilson"