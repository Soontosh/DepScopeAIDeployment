import os
import time
from typing import Any
from django.http import HttpRequest
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from live.models import Reports, User

@api_view(['POST'])
def generate_samples_endpoint(request: HttpRequest, user_id: int) -> Response:
    """
    Endpoint to generate sample reports for a given user.

    Args:
        request (HttpRequest): The HTTP request object.
        user_id (int): The ID of the user for whom to generate samples.

    Returns:
        Response: A JSON response indicating success or failure.
    """
    try:
        gen_samples_helper(user_id)  # Call the gen_samples_helper function with the user_id
        return Response({"message": "Samples generated successfully!"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def gen_samples_helper(user_id: int) -> None:
    """
    Helper function to generate sample reports for a given user.

    Args:
        user_id (int): The ID of the user for whom to generate samples.
    """
    # Get user object
    user = User.objects.get(id=user_id)

    # Get current working directory
    cwd = os.getcwd()

    # Join cwd with "samples" folder
    folder = os.path.join(cwd, "samples")

    # Loop through range of 4, starting at 1
    for i in range(1, 5):
        # Check if user already has a report with the same id
        if Reports.objects.filter(id=str(i), user=user).exists():
            print(f"Report {i} already exists.")
            # Check if the report.image does not contain "default"
            report = Reports.objects.get(id=str(i), user=user)
            if "default" not in report.image.name:
                # Replace the year in the date with 2023
                report.date = report.date.replace("2024", "2023")
                report.save()
                continue

        # Get current folder path
        folder_path = os.path.join(folder, f"p{i}")

        # Load report.html
        report_content = load_file_content(os.path.join(folder_path, "report.html"))

        # Load patient_name.txt
        patient_name = load_file_content(os.path.join(folder_path, "patient_name.txt"))

        # Generate random date between 1/1/2024 and 3/1/2024
        date = generate_random_date(i)

        # Get new URL
        new_url = f"/report/{str(i)}"

        # Create new report object
        report = Reports(
            id=str(i),
            user=user,
            patient_name=patient_name,
            report=report_content,
            url=new_url,
            date=date
        )

        # Print report URL for debugging
        print("Report URL: ", report.url)

        # Save the report
        report.save()

def load_file_content(file_path: str) -> str:
    """
    Loads the content of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    with open(file_path, "r") as file:
        return file.read()

def generate_random_date(index: int) -> str:
    """
    Generates a random date between 1/1/2024 and 3/1/2024.

    Args:
        index (int): The index to offset the date generation.

    Returns:
        str: The generated date in MM/DD/YYYY format.
    """
    return time.strftime("%m/%d/%Y", time.gmtime(time.time() + index * 60 * 60 * 24 * 30))