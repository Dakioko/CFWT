from django import forms
from ..models import ClimateFinanceData
from decimal import Decimal

class ClimateFinanceDataForm(forms.ModelForm):
    class Meta:
        model = ClimateFinanceData
        fields = ['project', 'funding_source', 'funding_type', 'total_amount', 'currency', 'status']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'funding_source': forms.Select(attrs={'class': 'form-control'}),
            'funding_type': forms.Select(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get("project")
        funding_source = cleaned_data.get("funding_source")
        funding_type = cleaned_data.get("funding_type")

        if project and funding_source and funding_type:
            if ClimateFinanceData.objects.filter(
                project=project,
                funding_source=funding_source,
                funding_type=funding_type
            ).exists():
                raise forms.ValidationError(
                    "This project/funding source/type combination already exists."
                )

        total_amount = cleaned_data.get("total_amount")
        if total_amount is not None and total_amount <= Decimal('0'):
            self.add_error('total_amount', "Amount must be greater than zero.")

        return cleaned_data

class DataImportForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.json'
        }),
        help_text="Supported formats: CSV, Excel (XLSX), JSON"
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            valid_extensions = ['.csv', '.xlsx', '.json']
            extension = file.name[file.name.rfind('.'):].lower()
            
            if extension not in valid_extensions:
                raise forms.ValidationError(
                    "Unsupported file format. Please upload a CSV, Excel (XLSX), or JSON file."
                )
            
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError("File too large. Maximum size is 5MB.")
                
        return file