from django import forms

class ImageUploadForm(forms.Form):
    """
    A form for uploading images associated with a specific report.

    Attributes:
        image (forms.ImageField): The image file to be uploaded.
        report_id (forms.TimeField): The ID of the report associated with the image, hidden from the user.
    """
    image: forms.ImageField = forms.ImageField()
    report_id: forms.TimeField = forms.TimeField(widget=forms.HiddenInput(), required=False)