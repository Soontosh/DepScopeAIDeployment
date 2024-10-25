import json
import requests
from requests.auth import HTTPBasicAuth
from typing import Tuple, Optional
from django.http import HttpRequest
from urllib.parse import urljoin
from depscope.settings import CLIENT_ID, CLIENT_SECRET

client_id = CLIENT_ID
client_secret = CLIENT_SECRET

def get_token(code: str, request: Optional[HttpRequest] = None) -> Tuple[str, str]:
    """
    Retrieves the access token and refresh token from Zoom using the authorization code.

    Args:
        code (str): The authorization code received from Zoom.
        request (Optional[HttpRequest]): The HTTP request object, used to construct the redirect URI.

    Returns:
        Tuple[str, str]: A tuple containing the access token and refresh token.
    """
    # Encode the client id and secret to base64
    client_auth = HTTPBasicAuth(client_id, client_secret)

    if request:
        # Construct the redirect URI based on the request host
        domain = request.get_host()
        redirect_uri = urljoin(f"http://{domain}", "/account_setup")
        post_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        }
    else:
        # Default to localhost redirect URI
        post_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:8000/account_setup"
        }

    # Make the POST request to Zoom's OAuth token endpoint
    response = requests.post("https://zoom.us/oauth/token", auth=client_auth, data=post_data)
    token_json = response.json()

    # Return the access token and refresh token
    return token_json['access_token'], token_json['refresh_token']

def refresh_token(refresh_token: str) -> Tuple[str, str]:
    """
    Refreshes the access token using the refresh token.

    Args:
        refresh_token (str): The refresh token received from Zoom.

    Returns:
        Tuple[str, str]: A tuple containing the new access token and refresh token.
    """
    # Encode the client id and secret to base64
    client_auth = HTTPBasicAuth(client_id, client_secret)

    post_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    # Make the POST request to Zoom's OAuth token endpoint
    response = requests.post("https://zoom.us/oauth/token", auth=client_auth, data=post_data)
    token_json = response.json()

    try:
        # Return the new access token and refresh token
        return token_json['access_token'], token_json["refresh_token"]
    except KeyError:
        # Handle the case where the expected keys are not in the response
        print("Key Error: ", token_json)
        raise