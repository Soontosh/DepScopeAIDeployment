from typing import Union
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from live.forms import ImageUploadForm
from live.models import Reports
import requests

def handle_post_request(request: HttpRequest, report_id: str) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Handles the POST request for uploading a profile picture.

    Args:
        request (HttpRequest): The HTTP request object.
        report_id (str): The ID of the report.

    Returns:
        Union[HttpResponseRedirect, HttpResponse]: A redirect response to the dashboard or the rendered upload template.
    """
    form = ImageUploadForm(request.POST, request.FILES)
    if form.is_valid():
        report = get_object_or_404(Reports, id=report_id)
        if report.user_id == request.session['user_id']:  # Check if the report belongs to the user stored in the session
            report.image = form.cleaned_data['image']
            report.save()
        return HttpResponseRedirect('/dashboard/')
    else:
        report = get_object_or_404(Reports, id=report_id)
        return render(request, 'upload.html', {'form': form, 'report': report})

def handle_get_request(request: HttpRequest, report_id: str) -> HttpResponse:
    """
    Handles the GET request for uploading a profile picture. Meant to render the upload template.

    Args:
        report_id (str): The ID of the report.

    Returns:
        HttpResponse: The rendered upload template.
    """
    form = ImageUploadForm()
    report = get_object_or_404(Reports, id=report_id)
    return render(request, 'upload.html', {'form': form, 'report': report})

def upload_pfp(request: HttpRequest, report_id: str) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Handles the upload of a profile picture for a patient.

    Args:
        request (HttpRequest): The HTTP request object.
        report_id (str): The ID of the report.

    Returns:
        Union[HttpResponseRedirect, HttpResponse]: A redirect response to the dashboard or the rendered upload template.
    """
    if request.method == 'POST':
        return handle_post_request(request, report_id)
    else:
        return handle_get_request(request, report_id)