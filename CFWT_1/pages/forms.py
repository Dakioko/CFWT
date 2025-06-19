from django import forms
from .models import ClimateFinanceData

class ClimateFinanceDataForm(forms.ModelForm):
    class Meta:
        model = ClimateFinanceData
        fields = ['project_name', 'funding_source', 'amount']

    def clean(self):
        cleaned_data = super().clean()
        project_name = cleaned_data.get("project_name")
        funding_source = cleaned_data.get("funding_source")
        amount = cleaned_data.get("amount")

        # Check for duplicate records in the database
        if ClimateFinanceData.objects.filter(
            project_name=project_name, funding_source=funding_source, amount=amount
        ).exists():
            raise forms.ValidationError("This record already exists in the database!")

        return cleaned_data

class DataImportForm(forms.Form):
    file = forms.FileField()
