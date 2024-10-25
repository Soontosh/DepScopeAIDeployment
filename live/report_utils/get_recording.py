""" Takes in therapist refresh code and id and returns the temp_mp4 and temp_vtt paths """
import requests
from live.utls import refresh_token
from live.models import User, Reports
import os
import time
from typing import Tuple

# Custom error for when the report already exists
class ReportAlreadyExists(Exception):
    pass

# Custom error for when no recordings are found
class NoRecordingsFound(Exception):
    pass

def get_access_token(refresh_code: str) -> Tuple[str, str]:
    """
    Retrieves the access token and new refresh token using the provided refresh code.

    Args:
        refresh_code (str): The refresh token.

    Returns:
        Tuple[str, str]: The access token and new refresh token.
    """
    return refresh_token(refresh_code)

def update_user_refresh_token(user: User, new_refresh_token: str) -> None:
    """
    Updates the user's refresh token and saves the user.

    Args:
        user (User): The user object.
        new_refresh_token (str): The new refresh token.
    """
    user.refresh_token = new_refresh_token
    user.save()

def get_recordings_list(access_token: str) -> dict:
    """
    Retrieves the list of recordings from the Zoom API.

    Args:
        access_token (str): The access token.

    Returns:
        dict: The JSON response containing the list of recordings.
    """
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    one_month_ago = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 2592000))
    response = requests.get(f'https://api.zoom.us/v2/users/me/recordings?from={one_month_ago}', headers=headers)
    return response.json()

def download_file(url: str, headers: dict, file_path: str) -> None:
    """
    Downloads a file from the given URL and saves it to the specified file path.

    Args:
        url (str): The URL to download the file from.
        headers (dict): The headers for the request.
        file_path (str): The path to save the downloaded file.
    """
    response = requests.get(url, headers=headers)
    with open(file_path, "wb") as f:
        f.write(response.content)

def get_recording(id: str, refresh_code: str) -> Tuple[str, str, str, str]:
    """
    Fetches a recording from the Zoom API given the user ID and refresh code.

    Args:
        id (str): The user ID.
        refresh_code (str): The refresh token.

    Returns:
        Tuple[str, str, str, str]: The paths to the MP4 and VTT files, the report ID, and the date of the meeting.

    Raises:
        ReportAlreadyExists: If the report already exists.
        NoRecordingsFound: If no recordings are found.
    """
    # Get the access token and new refresh token
    access_token, new_refresh_token = get_access_token(refresh_code)

    # Get the user and update the refresh token
    user = User.objects.get(id=id)
    update_user_refresh_token(user, new_refresh_token)

    # Get the list of recordings
    json_response = get_recordings_list(access_token)

    # Get the first MP4 recording file
    try:
        first_mp4_download_json = next((item for item in json_response["meetings"][0]["recording_files"] if item["file_type"] == "MP4"), None)
    except IndexError:
        print("error: ")
        print(json_response)
        raise NoRecordingsFound("No recordings found")

    # Check if the report already exists
    report = Reports.objects.filter(id=first_mp4_download_json['id']).first()
    if report:
        raise ReportAlreadyExists("Report already exists")

    # Get the first transcript file
    first_item_transcript = next((item for item in json_response["meetings"][0]["recording_files"] if item["file_type"] == "TRANSCRIPT"), None)

    # Get the current file's directory
    current_file_directory = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

    # Temp paths
    temp_mp4 = f"{current_file_directory}/temp_files/{first_mp4_download_json['id']}_meeting_recording.mp4"
    temp_vtt = f"{current_file_directory}/temp_files/{first_item_transcript['id']}_meeting_transcript.vtt"

    # Download the video and transcript
    download_file(first_mp4_download_json["download_url"], headers={'Authorization': f'Bearer {access_token}'}, file_path=temp_mp4)
    download_file(first_item_transcript["download_url"], headers={'Authorization': f'Bearer {access_token}'}, file_path=temp_vtt)

    # Get the date of the meeting and convert to mm/dd/yyyy format
    date = json_response["meetings"][0]["start_time"].split("T")[0]
    date = time.strftime("%m/%d/%Y", time.strptime(date, "%Y-%m-%d"))

    return temp_mp4, temp_vtt, first_mp4_download_json['id'], date