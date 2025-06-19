from django import forms
from ..models import FundingSource


# ------------------ FUNDING SOURCE FORM ------------------
class FundingSourceForm(forms.ModelForm):
    class Meta:
        model = FundingSource
        fields = ['name', 'type', 'country', 'contact_email', 'website']

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    def clean_country(self):
        country = self.cleaned_data.get("country")
        return country.strip().title() if country else country

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        country = cleaned_data.get("country")

        if name and country:
            existing = FundingSource.objects.filter(
                name__iexact=name.strip(),
                country__iexact=country.strip()
            )

            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise forms.ValidationError("This funding source already exists in the database!")

        return cleaned_data


# ------------------ FILE IMPORT FORM ------------------
class DataImportForm(forms.Form):
    file = forms.FileField(label="Upload a CSV, Excel (.xlsx), or JSON file")

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        valid_extensions = [".csv", ".xlsx", ".json"]

        if not any(uploaded_file.name.lower().endswith(ext) for ext in valid_extensions):
            raise forms.ValidationError("Only CSV, Excel (.xlsx), or JSON files are allowed.")

        return uploaded_file
