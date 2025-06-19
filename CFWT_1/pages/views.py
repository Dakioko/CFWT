from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import ClimateFinanceData
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django_tables2 import SingleTableView, RequestConfig
from .tables import ClimateFinanceTable
from django.db.models import Q
from django.http import HttpResponse
from .forms import DataImportForm
from django.contrib import messages
import csv
import pandas as pd
import json
from decimal import Decimal
from .forms import ClimateFinanceDataForm  
from django.db import IntegrityError
# ----------------- HOME PAGE -----------------
class HomePageView(TemplateView):
    template_name = 'home.html'

# ----------------- LIST DATA -----------------
class ClimateFinanceDataListView(SingleTableView):
    model = ClimateFinanceData
    table_class = ClimateFinanceTable
    template_name = "pages/data_list.html"
    paginate_by = 5  

    def get_queryset(self):
        query = self.request.GET.get('q')
        qs = ClimateFinanceData.objects.all()

        if query:
            qs = qs.filter(
                Q(project_name__icontains=query) |
                Q(funding_source__icontains=query) |
                Q(amount__icontains=query) |
                Q(created_at__icontains=query)
            )
        return qs

    def get_table(self, **kwargs):
        table = self.table_class(self.get_queryset(), request=self.request, **kwargs)
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

# ----------------- CREATE, UPDATE, DELETE -----------------
class ClimateFinanceDataCreateView(LoginRequiredMixin, CreateView):
    model = ClimateFinanceData
    fields = ['project_name', 'funding_source', 'amount']
    template_name = "pages/data_form.html"
    success_url = reverse_lazy('data_list')

class ClimateFinanceDataUpdateView(LoginRequiredMixin, UpdateView):
    model = ClimateFinanceData
    fields = ['project_name', 'funding_source', 'amount']
    template_name = "pages/data_edit.html"
    success_url = reverse_lazy('data_list')

class ClimateFinanceDeleteView(LoginRequiredMixin, DeleteView):
    model = ClimateFinanceData
    template_name = "pages/data_delete.html"
    success_url = reverse_lazy('data_list')

# ----------------- EXPORT DATA TO CSV -----------------
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="climate_finance_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Project Name', 'Funding Source', 'Amount', 'Created At'])  # Column Headers

    for data in ClimateFinanceData.objects.all():
        writer.writerow([data.project_name, data.funding_source, data.amount, data.created_at])

    return response

# ----------------- DOWNLOAD SAMPLE FILE -----------------
def download_sample(request):
    """Generate and return a sample CSV file for users to format their data correctly."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample_climate_finance.csv"'

    writer = csv.writer(response)
    writer.writerow(["Project Name", "Funding Source", "Amount"])  # Column headers
    writer.writerow(["Green Energy Project", "World Bank", "1000000"])
    writer.writerow(["Sustainable Water Initiative", "UNDP", "750000"])
    
    return response

# ----------------- IMPORT DATA (CSV, XLSX, JSON) -----------------
def import_data(request):
    if request.method == "POST":
        form = DataImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            file_name = file.name.lower()

            try:
                if file_name.endswith(".csv"):
                    imported_data, duplicates = handle_csv(file)
                elif file_name.endswith(".xlsx"):
                    imported_data, duplicates = handle_excel(file)
                elif file_name.endswith(".json"):
                    imported_data, duplicates = handle_json(file)
                else:
                    messages.error(request, "Invalid file format! Upload CSV, Excel, or JSON.")
                    return redirect("data_import")

                if duplicates:
                    messages.warning(request, f"Skipped {len(duplicates)} duplicate records.")

                if imported_data:
                    messages.success(request, f"Successfully imported {len(imported_data)} records.")
                else:
                    messages.info(request, "No new data was imported.")

            except Exception as e:
                messages.error(request, f"Error importing file: {str(e)}")

            return redirect("data_import")

    else:
        form = DataImportForm()
    
    return render(request, "pages/data_import.html", {"form": form})

# ----------------- HELPER FUNCTIONS -----------------
def handle_csv(file):
    """Handle CSV file import and check for duplicates."""
    decoded_file = file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(decoded_file)

    imported_data = []
    duplicates = []

    for row in reader:
        project_name = row["Project Name"].strip()
        funding_source = row["Funding Source"].strip()
        amount = Decimal(row["Amount"].strip())

        if not ClimateFinanceData.objects.filter(
            project_name__iexact=project_name,
            funding_source__iexact=funding_source,
            amount=amount
        ).exists():
            imported_data.append(ClimateFinanceData(
                project_name=project_name,
                funding_source=funding_source,
                amount=amount
            ))
        else:
            duplicates.append(row)

    ClimateFinanceData.objects.bulk_create(imported_data)
    return imported_data, duplicates

def handle_excel(file):
    """Handle Excel (XLSX) file import and check for duplicates."""
    df = pd.read_excel(file)
    imported_data = []
    duplicates = []

    for _, row in df.iterrows():
        project_name = str(row["Project Name"]).strip()
        funding_source = str(row["Funding Source"]).strip()
        amount = Decimal(str(row["Amount"]).strip())

        if not ClimateFinanceData.objects.filter(
            project_name__iexact=project_name,
            funding_source__iexact=funding_source,
            amount=amount
        ).exists():
            imported_data.append(ClimateFinanceData(
                project_name=project_name,
                funding_source=funding_source,
                amount=amount
            ))
        else:
            duplicates.append(row)

    ClimateFinanceData.objects.bulk_create(imported_data)
    return imported_data, duplicates

def handle_json(file):
    """Handle JSON file import and check for duplicates."""
    data = json.load(file)
    imported_data = []
    duplicates = []

    for row in data:
        project_name = row["Project Name"].strip()
        funding_source = row["Funding Source"].strip()
        amount = Decimal(row["Amount"])

        if not ClimateFinanceData.objects.filter(
            project_name__iexact=project_name,
            funding_source__iexact=funding_source,
            amount=amount
        ).exists():
            imported_data.append(ClimateFinanceData(
                project_name=project_name,
                funding_source=funding_source,
                amount=amount
            ))
        else:
            duplicates.append(row)

    ClimateFinanceData.objects.bulk_create(imported_data)
    return imported_data, duplicates

def add_data(request):
    if request.method == "POST":
        form = ClimateFinanceDataForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Data saved successfully!")
                return redirect('data_list')  # Redirect to data listing
            except IntegrityError:
                messages.error(request, "Duplicate record detected! This entry already exists.")
                return redirect('data_create')  # Redirect back to the form
    else:
        form = ClimateFinanceDataForm()
    
    return render(request, 'data_create.html', {'form': form})

from django.shortcuts import render
from .models import ClimateFinanceData
import json

def reports_view(request):
    data = ClimateFinanceData.objects.all()
    
    # Convert Decimal values to float for JSON serialization
    funding_sources = list(data.values_list('funding_source', flat=True))
    funding_amounts = [float(amount) for amount in data.values_list('amount', flat=True)]  # Convert Decimal to float
    
    project_names = list(data.values_list('project_name', flat=True))
    project_funding = [float(amount) for amount in data.values_list('amount', flat=True)]  # Convert Decimal to float
    
    # Example timeline data (should be replaced with real data if available)
    timeline_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]  
    timeline_data = [5000, 12000, 8000, 15000, 20000, 25000]  

    # Prepare context for rendering the template
    context = {
        "funding_sources": json.dumps(funding_sources),
        "funding_amounts": json.dumps(funding_amounts),
        "project_names": json.dumps(project_names),
        "project_funding": json.dumps(project_funding),
        "timeline_labels": json.dumps(timeline_labels),
        "timeline_data": json.dumps(timeline_data),
    }

    return render(request, "pages/reports.html", context)
