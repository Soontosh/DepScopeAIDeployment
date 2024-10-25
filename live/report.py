from typing import Dict
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Reports

def get_report_context(report_id: str) -> Dict[str, str]:
    """
    Retrieves the report context for rendering the HTML template.

    Args:
        report_id (str): The ID of the report.

    Returns:
        Dict[str, str]: A dictionary containing the report content.
    """
    # Retrieve the Report instance or return a 404 error if not found
    report = get_object_or_404(Reports, id=report_id)

    # Prepare the context dictionary
    context = {
        'report': report.report,
    }

    return context

def report(request: HttpRequest, report_id: str) -> HttpResponse:
    """
    Renders the report into an HTML template.

    Args:
        request (HttpRequest): The HTTP request object.
        report_id (str): The ID of the report.

    Returns:
        HttpResponse: The rendered HTML template with the report content.
    """
    # Get the report context
    context = get_report_context(report_id)

    # Render the HTML template with the report content
    return render(request, "new_report.html", context)