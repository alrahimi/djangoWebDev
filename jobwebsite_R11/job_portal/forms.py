from pathlib import Path

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from .models import Application


MAX_RESUME_SIZE_MB = 5
MAX_RESUME_SIZE_BYTES = MAX_RESUME_SIZE_MB * 1024 * 1024
ALLOWED_RESUME_EXTENSIONS = ['pdf', 'doc', 'docx', 'txt']


def validate_resume_size(uploaded_file):
    if uploaded_file.size > MAX_RESUME_SIZE_BYTES:
        raise ValidationError(
            f"Resume file is too large. Maximum allowed size is {MAX_RESUME_SIZE_MB} MB."
        )


class ApplicationForm(forms.ModelForm):
    resume = forms.FileField(
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_RESUME_EXTENSIONS),
            validate_resume_size,
        ],
        help_text=f"Accepted formats: {', '.join(ALLOWED_RESUME_EXTENSIONS).upper()}. Maximum size: {MAX_RESUME_SIZE_MB} MB.",
    )

    class Meta:
        model = Application
        fields = ['applicant_name', 'email', 'resume']
        widgets = {
            'applicant_name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
        }

    def clean_resume(self):
        resume = self.cleaned_data['resume']
        extension = Path(resume.name).suffix.lower().lstrip('.')

        # FileExtensionValidator checks this too, but this keeps the error clear
        # even when a browser sends an unusual filename/case combination.
        if extension not in ALLOWED_RESUME_EXTENSIONS:
            raise ValidationError(
                f"Unsupported resume format. Use one of: {', '.join(ALLOWED_RESUME_EXTENSIONS).upper()}."
            )
        return resume
