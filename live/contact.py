from django.template import loader
from django.http import HttpRequest, HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives
from depscope.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, STAFF_EMAIL
from django.shortcuts import render
import dotenv, os

dotenv.load_dotenv()

STAFF_EMAIL = os.getenv("STAFF_EMAIL")

def contact(request: HttpRequest) -> HttpResponse:
    """
    Renders the contact form template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered contact form template.
    """
    template = loader.get_template('contact.html')

    return render(request, 'contact.html', {'STAFF_EMAIL': STAFF_EMAIL})

def build_email_message(name: str, from_email: str, subject: str, comments: str) -> EmailMultiAlternatives:
    """
    Builds the email message to be sent.

    Args:
        name (str): The name of the sender.
        from_email (str): The email address of the sender.
        subject (str): The subject of the email.
        comments (str): The body of the email.

    Returns:
        EmailMultiAlternatives: The constructed email message.
    """
    # Add line under comments saying who the email is from
    comments += f"\n\nThis email was sent by {name} at {from_email} through the contact form on the Depscope website."
    return EmailMultiAlternatives(subject, comments, EMAIL_HOST_USER, [STAFF_EMAIL])

@api_view(['POST'])
def send_email(request: HttpRequest) -> Response:
    """
    Handles the sending of an email through the contact form.

    Args:
        request (HttpRequest): The HTTP request object containing form data.

    Returns:
        Response: A JSON response indicating the result of the form submission.
    """
    # Extract form data from the request
    name = request.data.get('name')
    from_email = request.data.get('email')
    subject = request.data.get('subject')
    comments = request.data.get('comments')

    # Build the email message
    email_message = build_email_message(name, from_email, subject, comments)

    # Establish the email connection and send the message
    connection = get_connection(username=EMAIL_HOST_USER, password=EMAIL_HOST_PASSWORD, fail_silently=False)
    connection.send_messages([email_message])

    # Prepare the response data
    response_data = {
        'message': 'Form submitted successfully!',
        'name': name,
        'email': from_email,
        'subject': subject,
        'comments': comments
    }
    print(response_data)  # Debugging purpose

    # Return the response
    return Response(response_data)