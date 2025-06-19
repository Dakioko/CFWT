import django_tables2 as tables
from django.utils.html import format_html
from django.urls import reverse
from django_tables2.config import RequestConfig  
from .models import (Sector, FundingSource, Recipient, ClimateProject, ClimateFinanceData, Disbursement
)

class BaseTable(tables.Table):
    actions = tables.Column(empty_values=(), verbose_name="Actions", orderable=False)
    
    class Meta:
        template_name = "django_tables2/bootstrap5.html"
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        
        if request:
            RequestConfig(request, paginate={"per_page": 10}).configure(self)
            if not request.user.is_authenticated:
                self.exclude = ("actions",)

    def render_actions(self, record):
        update_url = reverse(f'{self.Meta.model._meta.model_name}_update', args=[record.pk])
        delete_url = reverse(f'{self.Meta.model._meta.model_name}_delete', args=[record.pk])

        return format_html(
            '<a href="{}" class="btn btn-sm btn-outline-primary"><i class="bi bi-pencil"></i></a> '
            '<button type="button" class="btn btn-sm btn-outline-danger" data-bs-toggle="modal" '
            'data-bs-target="#deleteModal" data-delete-url="{}" data-name="{}">'
            '<i class="bi bi-trash"></i></button>',
            update_url,
            delete_url,
            record.name if hasattr(record, "name") else "this record"
        )

class SectorTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Sector
        fields = ("name", "description")
        
class FundingSourceTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = FundingSource
        fields = ("name", "type", "country", "contact_email", "website")  # Include all relevant fields
        

class RecipientTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Recipient
        fields = ("name", "type", "location", "contact_email")

class ClimateProjectTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = ClimateProject
        fields = ("name", "description", "recipient","sector","start_date", "end_date")

class ClimateFinanceTable(BaseTable):
    def render_total_amount(self, value):
        return f"Ksh. {value:,.2f}"
    
    class Meta(BaseTable.Meta):
        model = ClimateFinanceData
        fields = ("project", "funding_source", "funding_type", "total_amount", "currency", "status")

class DisbursementTable(BaseTable):
    def render_amount(self, value):
        return f"Ksh. {value:,.2f}"  # Formatting amount with commas and 2 decimal places
    
    class Meta(BaseTable.Meta):
        model = Disbursement
        fields = ("finance_data.project", "amount", "currency", "disbursement_date", "notes")
        attrs = {"class": "table table-striped table-hover"}  # Bootstrap Styling
