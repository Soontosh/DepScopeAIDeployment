from typing import Dict, Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
import requests
import json
from .models import User, Reports
from depscope.settings import MEDIA_ROOT
from django.conf import settings
from typing import Tuple
from depscope.settings import ZOOM_PRO

def get_user_id_from_session(request: HttpRequest) -> int:
    """
    Retrieves the user ID from the session.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        int: The user ID.
    """
    return request.session['user_id']

def generate_report(user_id: int) -> Dict[str, Any]:
    """
    Generates a report by making a call to the /generate_report/ endpoint.

    Args:
        user_id (int): The ID of the user.

    Returns:
        Dict[str, Any]: A dictionary containing the response data.
    """
    data = {"therapist_id": user_id}
    response = requests.post('http://localhost:8000/generate_report/', json=data)
    return response

def handle_response(response: requests.Response) -> Tuple[int, bool]:
    """
    Handles the response from the /generate_report/ endpoint.

    Args:
        response (requests.Response): The response object.

    Returns:
        Tuple[int, bool]: A tuple containing the number of generated reports and an error flag.
    """
    error = False
    generated = 0

    if response.status_code != 200:
        try:
            generated = response.json().get("num_generated", 0)
        except json.decoder.JSONDecodeError:
            error = True
            print("Error: ", response.text)
    else:
        generated = response.json().get("num_generated", 0)

    return generated, error

def get_user_reports(user_id: int) -> Tuple[User, Any]:
    """
    Retrieves the user and their reports from the database.

    Args:
        user_id (int): The ID of the user.

    Returns:
        Tuple[User, Any]: A tuple containing the user object and their reports.
    """
    user = User.objects.get(id=user_id)
    reports = Reports.objects.filter(user=user)
    return user, reports

def dashboard(request: HttpRequest) -> HttpResponse:
    """
    Renders the clinician's dashboard with user reports and generated report count.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered dashboard template.
    """
    print("MEDIA ROOT: ", MEDIA_ROOT)
    print("ZOOM_PRO: ", ZOOM_PRO)

    # Get the user's ID from the session
    user_id = get_user_id_from_session(request)
    
    if ZOOM_PRO: # Run retrieval of reports and report generation only if ZOOM_PRO is enabled

        # Generate the report
        response = generate_report(user_id)
        generated, error = handle_response(response)
    else: # Otherwise, set the number of generated reports and error flag to default values
        # Set the number of generated reports and error flag
        generated = 0
        error = False

        # Get the user and their reports
        user, reports = get_user_reports(user_id)

        print("Zoom Pro is not enabled, setting default values for dashboard")

    # Render the dashboard template
    return render(request, "dashboard.html", {"reports": reports, "user": user, "generated": generated, "error": error})