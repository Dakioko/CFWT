from django import forms
from ..models import Disbursement
from django.core.validators import MinValueValidator

class DisbursementForm(forms.ModelForm):
    disbursement_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Date when funds were actually disbursed"
    )
    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Amount disbursed (must be positive)"
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Any additional information about this disbursement"
    )

    class Meta:
        model = Disbursement
        fields = ['finance_data', 'amount', 'currency', 'disbursement_date', 'notes']
        widgets = {
            'currency': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'finance_data': 'Related climate finance project/data',
            'currency': 'Currency of the disbursed amount',
        }

    def clean(self):
        cleaned_data = super().clean()
        finance_data = cleaned_data.get("finance_data")
        disbursement_date = cleaned_data.get("disbursement_date")
        amount = cleaned_data.get("amount")

        if not all([finance_data, disbursement_date, amount]):
            return cleaned_data  # Let other validators handle missing fields

        queryset = Disbursement.objects.filter(
            finance_data=finance_data,
            disbursement_date=disbursement_date,
            amount=amount
        )

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                "A disbursement with these exact details already exists in the database!"
            )

        return cleaned_data


class DataImportForm(forms.Form):
    file = forms.FileField(
        label="CSV File",
        help_text="Upload a CSV file with disbursement data",
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )