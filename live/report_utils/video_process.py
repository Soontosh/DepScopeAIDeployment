""" TAKES IN MP4 PATH AND VTT DATA AND MFCCS, RETURNS AUS AND UPDATED MFCCS AND TEMP mp4 FILE AND TEMP FRAMES AND TEMP OUTPUT """
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
import os
import PIL.Image as Image
import subprocess
import shlex
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Any
from joblib import load

def extract_patient_speaking_times(vtt_data: Dict[str, Dict[str, Any]]) -> List[Tuple[float, float]]:
    """
    Extracts the start and end times of the patient's utterances from VTT data.

    Args:
        vtt_data (Dict[str, Dict[str, Any]]): The VTT data containing speaker and timing information.

    Returns:
        List[Tuple[float, float]]: A list of tuples containing the start and end times of the patient's utterances.
    """
    patient_speaking_times = []
    for key in vtt_data:
        if vtt_data[key]["speaker"] == "Patient":
            patient_speaking_times.append((vtt_data[key]["start_time"], vtt_data[key]["end_time"]))
    return patient_speaking_times

def concatenate_patient_clips(mp4_path: str, speaking_times: List[Tuple[float, float]]) -> VideoFileClip:
    """
    Concatenates video clips corresponding to the patient's speaking times.

    Args:
        mp4_path (str): The path to the MP4 file.
        speaking_times (List[Tuple[float, float]]): The start and end times of the patient's utterances.

    Returns:
        VideoFileClip: The concatenated video clip of the patient's utterances.
    """
    clips = []
    for start, end in speaking_times:
        clip = VideoFileClip(mp4_path).subclip(start, end)
        clips.append(clip)
    return concatenate_videoclips(clips)

def save_temp_files(concatenated_clip: VideoFileClip, recording_id: str) -> Tuple[str, str, str]:
    """
    Saves the concatenated video clip and creates temporary directories for frames and output.

    Args:
        concatenated_clip (VideoFileClip): The concatenated video clip of the patient's utterances.
        recording_id (str): The recording ID.

    Returns:
        Tuple[str, str, str, str]: The paths to the temporary mp4 file, frames directory, output directory, and OpenFace FeatureExtraction.exe.
    """
    current_file_directory = os.path.dirname(os.path.realpath(__file__))
    temp_mp4 = f"{current_file_directory}/temp_files/{recording_id}_meeting_video.mp4"
    temp_frames_dir = f"{current_file_directory}/temp_files/{recording_id}_frames"
    temp_output_dir = f"{current_file_directory}/temp_files/{recording_id}_output"

    concatenated_clip.write_videofile(temp_mp4)
    os.makedirs(temp_frames_dir, exist_ok=True)
    os.makedirs(temp_output_dir, exist_ok=True)

    # Get current file directory
    current_file_directory = os.path.dirname(os.path.realpath(__file__))

    # Construct the path to FeatureExtraction.exe, which is used to extract AUs
    feature_extraction_path = os.path.abspath(os.path.join(current_file_directory, '..', '..', 'OpenFace', 'FeatureExtraction.exe'))

    return temp_mp4, temp_frames_dir, temp_output_dir, feature_extraction_path

def extract_aus(temp_mp4: str, temp_frames_dir: str, temp_output_dir: str, feature_extraction_path: str) -> np.ndarray:
    """
    Extracts Action Units (AUs) from the video using OpenFace.

    Args:
        temp_mp4 (str): The path to the temporary mp4 file.
        temp_frames_dir (str): The path to the temporary frames directory.
        temp_output_dir (str): The path to the temporary output directory.
        feature_extraction_path (str): The absolute path to the OpenFace FeatureExtraction executable.

    Returns:
        np.ndarray: The extracted AUs.
    """

    # Run AU extraction using OpenFace
    command = f"{feature_extraction_path} -f {temp_mp4} -out_dir {temp_output_dir} -aus"

    # Check if all the files exist, print whether or not they exist
    for file in [temp_mp4, temp_frames_dir, temp_output_dir, feature_extraction_path]:
        print(f"Does {file} exist? {os.path.exists(file)}")

    print("aus generation command: ", command.replace("\\", "/"))

    subprocess.run(shlex.split(command.replace("\\", "/")), shell = True)

    # Load the extracted AUs
    aus_file = os.path.join(temp_output_dir, "temp_meeting_video.csv")
    print("aus_file before replace: ", aus_file)
    print("aus_file after replace: ", aus_file.replace("\\", "/"))
    aus_data = pd.read_csv(aus_file.replace("\\", "/"))

    return aus_data.to_numpy()

def video_process(mp4_path: str, vtt_data: Dict[str, Dict[str, Any]], mfccs: np.ndarray) -> Tuple[np.ndarray, np.ndarray, str, str, str]:
    """
    Processes video data to extract AUs and update MFCCs.

    Args:
        mp4_path (str): The path to the MP4 file.
        vtt_data (Dict[str, Dict[str, Any]]): The VTT data containing speaker and timing information.
        mfccs (np.ndarray): The MFCC features.

    Returns:
        Tuple[np.ndarray, np.ndarray, str, str, str]: The extracted AUs, updated MFCCs, path to the temporary mp4 file, frames directory, and output directory.
    """
    # Extract the patient's speaking times from the VTT data
    patient_speaking_times = extract_patient_speaking_times(vtt_data)

    # Concatenate the patient's video clips
    concatenated_clip = concatenate_patient_clips(mp4_path, patient_speaking_times)

    # Save the concatenated video clip and create temporary directories
    temp_mp4, temp_frames_dir, temp_output_dir, feature_extraction_path = save_temp_files(concatenated_clip, recording_id="temp")

    # Extract AUs from the video
    aus = extract_aus(temp_mp4, temp_frames_dir, temp_output_dir, feature_extraction_path)

    # Normalize the AUs
    scaler = load("scaler.joblib")
    aus = scaler.transform(aus)

    # Update MFCCs (this step is not detailed in the provided code, so it's assumed to be a placeholder)
    updated_mfccs = mfccs  # Placeholder for actual MFCC update logic

    return aus, updated_mfccs, temp_mp4, temp_frames_dir, temp_output_dir