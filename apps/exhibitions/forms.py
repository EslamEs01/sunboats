from django import forms

from .models import ExhibitionRequest


class ExhibitionRequestForm(forms.ModelForm):
    class Meta:
        model = ExhibitionRequest
        fields = (
            "name",
            "email",
            "phone",
            "country",
            "title",
            "medium",
            "description",
            "image",
        )
        labels = {
            "name": "Name",
            "email": "Email",
            "phone": "Phone",
            "country": "Country",
            "title": "Artwork title",
            "medium": "Medium",
            "description": "Short description",
            "image": "Image",
        }
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel"}),
            "country": forms.TextInput(attrs={"autocomplete": "country-name"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }
