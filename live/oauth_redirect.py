from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from depscope.settings import CLIENT_ID

def get_redirect_uri(request: HttpRequest) -> str:
    """
    Constructs the redirect URI based on the environment.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        str: The constructed redirect URI.
    """
    if settings.DEBUG or request.get_host() == "127.0.0.1:8000":
        return "http://localhost:8000/account_setup"
    else:
        scheme = "https" if request.is_secure() else "http"
        return f"{scheme}://{request.get_host()}/account_setup"

def oauth_redirect(request: HttpRequest) -> HttpResponse:
    """
    Redirects the user to the Zoom OAuth authorization page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect response to the Zoom OAuth authorization page.
    """
    # Get the redirect URI
    redirect_uri = get_redirect_uri(request)

    # Construct the Zoom OAuth URL
    zoom_oauth_url = f'https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={redirect_uri}'

    # Redirect to the Zoom OAuth authorization page
    return redirect(zoom_oauth_url)