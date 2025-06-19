from django import forms
from ..models import Sector


# ------------------ SECTOR FORM ------------------
class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ['name', 'description']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")

        if Sector.objects.filter(name__iexact=name).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
            raise forms.ValidationError("This sector already exists in the database!")

        return cleaned_data
    

# ------------------ FILE IMPORT FORM ------------------
class DataImportForm(forms.Form):
    file = forms.FileField()