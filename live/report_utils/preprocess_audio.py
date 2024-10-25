""" TAKES IN MP4 PATH AND VTT DATA DICTIONARY AND RECORDING ID, RETURNS MFCC FEATURES, TEMPORARY WAV FILE """
import os
import gc
import librosa
import numpy as np
from pydub import AudioSegment
from pydub.utils import make_chunks
from typing import Dict, Tuple, List
from live.models import Reports
from typing import Any
from speechpy.processing import cmvn

def extract_mfcc_features_audio_segment(audio_segment: AudioSegment) -> np.ndarray:
    """
    Extracts MFCC features from an audio segment.

    Args:
        audio_segment (AudioSegment): The audio segment from which to extract MFCC features.

    Returns:
        np.ndarray: The extracted MFCC features.
    """
    y = np.frombuffer(audio_segment._data, dtype=np.int16).astype(np.float32) / 2**15
    mfcc = librosa.feature.mfcc(y=y, sr=audio_segment.frame_rate, n_mfcc=60, n_fft=1980, hop_length=495)
    print(mfcc.shape)
    return mfcc

def get_patient_speaking_times(vtt_data: Dict[str, Dict[str, Any]]) -> List[Tuple[float, float]]:
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

def concatenate_patient_audio(audio: AudioSegment, speaking_times: List[Tuple[float, float]]) -> AudioSegment:
    """
    Concatenates the audio segments corresponding to the patient's speaking times.

    Args:
        audio (AudioSegment): The full audio segment.
        speaking_times (List[Tuple[float, float]]): The start and end times of the patient's utterances.

    Returns:
        AudioSegment: The concatenated audio segment of the patient's utterances.
    """
    new_audio = AudioSegment.empty()
    for start, end in speaking_times:
        new_audio += audio[int(start * 1000):int(end * 1000)]
    return new_audio

def get_mfccs(mp4_path: str, vtt_data: Dict[str, Dict[str, Any]], recording_id: str) -> Tuple[np.ndarray, str]:
    """
    Preprocesses audio data and derives MFCC features for the ML model.

    Args:
        mp4_path (str): The path to the MP4 file.
        vtt_data (Dict[str, Dict[str, Any]]): The VTT data containing speaker and timing information.
        recording_id (str): The recording ID.

    Returns:
        Tuple[np.ndarray, str]: The MFCC features and the path to the temporary WAV file.
    """
    # Load the video
    video = AudioSegment.from_file(mp4_path, format="mp4")

    # Get the current file's directory
    current_file_directory = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

    # Path to the temporary WAV file
    temp_wav = f"{current_file_directory}/temp_files/{recording_id}_meeting_audio.wav"

    # Export the audio to a WAV file
    video.export(temp_wav, format="wav")

    # Delete the video object to free memory
    del video
    gc.collect()

    # Extract the patient's speaking times from the VTT data
    patient_speaking_times = get_patient_speaking_times(vtt_data)

    # Load the audio from the temporary WAV file
    audio = AudioSegment.from_file(temp_wav, format="wav")

    # Concatenate the patient's audio segments
    audio = concatenate_patient_audio(audio, patient_speaking_times)

    # Export the concatenated audio back to the temporary WAV file
    audio.export(temp_wav, format="wav")

    # Split the audio into chunks of 7920ms
    chunks = make_chunks(audio, 7920)

    # Discard the last chunk if it is not exactly 7920ms
    if len(chunks[-1]) != 7920:
        chunks = chunks[:-1]

    # List to store the MFCC features
    mfccs = []

    # Extract MFCC features from each chunk
    for chunk in chunks:
        mfccs.append(extract_mfcc_features_audio_segment(chunk))

    # Convert the list of MFCCs to a NumPy array
    mfccs = np.array(mfccs)

    # Reshape the MFCCs for normalization
    shape = mfccs.shape[1:]  # Save the shape of MFCCs
    shape = (shape[1], shape[0])  # Swap the second and third axes
    mfccs = mfccs.reshape(mfccs.shape[0], -1)

    # Normalize the MFCCs
    mfccs = cmvn(mfccs, variance_normalization=True)

    # Reshape the MFCCs back to their original shape
    mfccs = mfccs.reshape(-1, *shape)

    return mfccs, temp_wav