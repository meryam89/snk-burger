from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label="Prénom",
        max_length=150,
    )

    last_name = forms.CharField(
        label="Nom",
        max_length=150,
    )

    email = forms.EmailField(
        label="Adresse e-mail",
        required=True,
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Cette adresse e-mail est déjà utilisée."
            )

        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
        ]

        labels = {
            "first_name": "Prénom",
            "last_name": "Nom",
            "email": "Adresse e-mail",
        }

    def clean_email(self):
        email = self.cleaned_data["email"]

        email_exists = User.objects.filter(
            email__iexact=email
        ).exclude(
            id=self.instance.id
        ).exists()

        if email_exists:
            raise forms.ValidationError(
                "Cette adresse e-mail est déjà utilisée."
            )

        return email