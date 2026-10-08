from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order

        fields = [
            "customer_name",
            "email",
            "phone",
            "address",
            "city",
            "postal_code",
            "notes",
        ]

        widgets = {
            "customer_name": forms.TextInput(
                attrs={
                    "placeholder": "Votre nom complet",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "exemple@email.com",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "06 00 00 00 00",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "placeholder": "Numéro et nom de rue",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "placeholder": "Votre ville",
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "placeholder": "Code postal",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Code d’entrée, étage...",
                }
            ),
        }