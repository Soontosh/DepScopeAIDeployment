from django.db import models

class User(models.Model):
    """
    Represents a user in the system.

    Attributes:
        id (models.TextField): The primary key for the user, fetched from the Zoom API.
        email (models.TextField): The email address of the user.
        first_name (models.CharField): The first name of the user.
        last_name (models.CharField): The last name of the user.
        refresh_token (models.TextField): The refresh token for the user's Zoom OAuth.
        plan (models.CharField): The subscription plan of the user: Basic, Professoinal, or Enterprise
    """
    id: models.TextField = models.TextField(primary_key=True)
    email: models.TextField = models.TextField()
    first_name: models.CharField = models.CharField(max_length=64)
    last_name: models.CharField = models.CharField(max_length=64)
    refresh_token: models.TextField = models.TextField()
    plan: models.CharField = models.CharField(
        max_length=15,
        choices=[("Basic", "Basic"), ("Professional", "Professional"), ("Enterprise", "Enterprise")],
        default="Basic"
    )

class Reports(models.Model):
    """
    Represents a report generated for a patient.

    Attributes:
        id (models.TextField): The primary key for the report.
        user (models.ForeignKey): The user who generated the report.
        patient_name (models.CharField): The name of the patient.
        report (models.TextField): The content of the report.
        url (models.TextField): The URL of the report.
        date (models.CharField): The date the report was generated.
        image (models.ImageField): The image associated with the report.
    """
    id: models.TextField = models.TextField(primary_key=True)
    user: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)
    patient_name: models.CharField = models.CharField(max_length=64)
    report: models.TextField = models.TextField()
    url: models.TextField = models.TextField()
    date: models.CharField = models.CharField(max_length=10)
    image: models.ImageField = models.ImageField(upload_to='reports/', default='\\default.png')

class NewsletterRecipients(models.Model):
    """
    Represents a recipient of the newsletter.

    Attributes:
        email (models.TextField): The email address of the recipient.
        subscribed (models.BooleanField): Whether the recipient is subscribed to the newsletter.
    """
    email: models.TextField = models.TextField(primary_key=True)
    subscribed: models.BooleanField = models.BooleanField(default=True)