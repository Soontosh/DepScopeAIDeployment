from typing import Tuple
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
import requests
from .models import User
from .utls import get_token, refresh_token

def get_code_from_url(url: str) -> str:
    """
    Extracts the Zoom authorization code from the URL.

    Args:
        url (str): The full URL containing the authorization code.

    Returns:
        str: The extracted authorization code.
    """
    return url.split('code=')[1]

def fetch_zoom_user_info(token: str) -> dict:
    """
    Fetches user information from Zoom API using the provided token.

    Args:
        token (str): The access token for Zoom API.

    Returns:
        dict: A dictionary containing user information.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get('https://api.zoom.us/v2/users/me', headers=headers)
    return response.json()

def account_setup(request: HttpRequest) -> HttpResponse:
    """
    Handles the account setup process by fetching user information from Zoom API
    and saving it to the database.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect response to the dashboard.
    """
    # Get the request URL
    url = request.build_absolute_uri()

    # Extract the authorization code from the URL
    code = get_code_from_url(url)

    # Create a new user instance
    user = User()

    # Get the access token and refresh token
    token, code = get_token(code, request=request)
    token, code = refresh_token(code)

    # Fetch user information from Zoom API
    user_info = fetch_zoom_user_info(token)

    # Populate the user instance with fetched information
    user.id = user_info["id"]
    user.email = user_info["email"]
    user.first_name = user_info["first_name"]
    user.last_name = user_info["last_name"]

    # Set the user's refresh token
    user.refresh_token = code

    # Save the user instance to the database
    user.save()

    # Store the user ID in the session and redirect to the dashboard
    request.session['user_id'] = user.id
    return redirect('/dashboard')