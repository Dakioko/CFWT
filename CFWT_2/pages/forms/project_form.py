from django import forms
from ..models import ClimateProject
# ------------------ CLIMATE PROJECT FORM ------------------
class ClimateProjectForm(forms.ModelForm):
    class Meta:
        model = ClimateProject
        fields = ['name', 'description', 'recipient', 'sector', 'start_date', 'end_date']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        recipient = cleaned_data.get("recipient")

        if ClimateProject.objects.filter(name__iexact=name, recipient=recipient).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
            raise forms.ValidationError("This climate project already exists in the database!")

        return cleaned_data
    
# ------------------ FILE IMPORT FORM ------------------
class DataImportForm(forms.Form):
    file = forms.FileField()