from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django_tables2.views import SingleTableView
from ..models import Disbursement  # Import Disbursement model
from ..tables import DisbursementTable  # Import DisbursementTable
from ..forms.disbursment_form import DisbursementForm
from django.http import HttpResponse
from django.contrib import messages
import csv
import pandas as pd

class DisbursementListView(SingleTableView):
    model = Disbursement
    template_name = "disbursement/disbursement_list.html"  # Updated template name
    table_class = DisbursementTable
    context_object_name = "disbursements"
    paginate_by = 10  # Pagination for better UI experience

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()  # Get and clean search query
        qs = Disbursement.objects.all()  # Fetch all disbursements

        if query:
            qs = qs.filter(
                Q(finance_data__project__name__icontains=query) |  # Search by project name (via finance_data)
                Q(amount__icontains=query) |  # Search by amount
                Q(currency__icontains=query) |  # Search by currency
                Q(disbursement_date__icontains=query) |  # Search by disbursement date
                Q(notes__icontains=query)  # Search by notes
            )

        return qs


# Disbursement Detail View
class DisbursementDetailView(LoginRequiredMixin, DetailView):
    model = Disbursement
    template_name = "disbursement/disbursement_detail.html"
    context_object_name = "disbursement"

# Disbursement Create View
class DisbursementCreateView(LoginRequiredMixin, CreateView):
    model = Disbursement
    form_class = DisbursementForm
    template_name = "disbursement/disbursement_form.html"
    success_url = reverse_lazy("disbursement_list")

# Disbursement Update View
class DisbursementUpdateView(LoginRequiredMixin, UpdateView):
    model = Disbursement
    form_class = DisbursementForm
    template_name = "disbursement/disbursement_form.html"
    success_url = reverse_lazy("disbursement_list")

# Disbursement Delete View
class DisbursementDeleteView(LoginRequiredMixin, DeleteView):
    model = Disbursement
    template_name = "disbursement/disbursement_confirm_delete.html"
    success_url = reverse_lazy("disbursement_list")


# ----------------- EXPORT DATA TO CSV -----------------
def export_csv_dis(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Disbursments.csv"'

    writer = csv.writer(response)
    writer.writerow(['Finance Data', 'Amount', 'Currency', 'Disbursment Date', 'Notes'])

    for disbursement in Disbursement.objects.all().select_related('finance_data'):
        writer.writerow([
            str(disbursement.finance_data),  # Finance Data
            disbursement.amount,             # Amount
            disbursement.currency,           # Currency
            disbursement.disbursement_date.strftime('%Y-%m-%d'),  # Disbursment Date
            disbursement.notes or ""         # Notes
        ])

    return response