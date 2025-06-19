from django import forms
from ..models import Recipient

class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['name', 'type', 'location', 'contact_email']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        type_ = cleaned_data.get("type")
        location = cleaned_data.get("location")
        contact_email = cleaned_data.get("contact_email")

        # Check for duplicate records
        if Recipient.objects.filter(
            name=name,
            type=type_,
            location=location,
            contact_email=contact_email if contact_email else None
        ).exists():
            raise forms.ValidationError("This recipient already exists in the database!")

        return cleaned_data


# ------------------ FILE IMPORT FORM ------------------
class DataImportForm(forms.Form):
    file = forms.FileField()
    
    
