import django_tables2 as tables
from .models import ClimateFinanceData
from django.utils.html import format_html
from django.urls import reverse
from django_tables2.config import RequestConfig  # ✅ Ensure pagination works

class ClimateFinanceTable(tables.Table):
    project_name = tables.Column(orderable=True)
    funding_source = tables.Column(orderable=True)
    amount = tables.Column(orderable=True)
    actions = tables.Column(empty_values=(), verbose_name="Actions", orderable=False)
    
    # Custom render method for the Amount column
    def render_amount(self, value):
        return f"Ksh. {value:,.2f}"  # Format with KSH and commas

    class Meta:
        model = ClimateFinanceData
        template_name = "django_tables2/bootstrap5.html"
        fields = ("project_name", "funding_source", "amount")  # Display only these fields

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)  # Extract request object
        super().__init__(*args, **kwargs)

        if request:
            RequestConfig(request, paginate={"per_page": 5}).configure(self)  # ✅ Fix Pagination
            if not request.user.is_authenticated:
                self.exclude = ("actions",)  # Hide actions for unauthenticated users

    def render_actions(self, record):
        update_url = reverse('data_update', args=[record.pk])
        delete_url = reverse('data_delete', args=[record.pk])

        return format_html(
            '<a href="{}" class="btn btn-sm btn-outline-primary"><i class="bi bi-pencil"></i></a> '
            '<a href="{}" class="btn btn-sm btn-outline-danger"><i class="bi bi-trash"></i></a>',
            update_url,
            delete_url
        )