from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import NewsletterRecipients
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import status
from django.http import HttpRequest

@api_view(["POST"])
def newsletter(request: HttpRequest) -> Response:
    """
    REST API Endpoint which receives an email and saves it to the database.

    Args:
        request (HttpRequest): The HTTP request object containing the email data.

    Returns:
        Response: A JSON response indicating success or failure.
    """
    try:
        json_data = request.data
        email = json_data["email"]

        # Validate the email format
        if not is_valid_email(email):
            return Response({
                "message": "Invalid email format",
                "success": False
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save the email to the database
        save_email_to_db(email)

        return Response({
            "message": "Email added to newsletter list",
            "success": True
        }, status=status.HTTP_201_CREATED)

    except ValidationError as e:
        return Response({
            "message": str(e),
            "success": False
        }, status=status.HTTP_400_BAD_REQUEST)

    except IntegrityError:
        return Response({
            "message": "Email already exists in the newsletter list",
            "success": False
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "message": "An unexpected error occurred: " + str(e),
            "success": False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def is_valid_email(email: str) -> bool:
    """
    Validates the email format.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email format is valid, False otherwise.
    """
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def save_email_to_db(email: str) -> None:
    """
    Saves the email to the newsletter recipients database.

    Args:
        email (str): The email address to save.

    Raises:
        IntegrityError: If the email already exists in the database.
    """
    recipient = NewsletterRecipients(email=email, subscribed=True)
    recipient.save()