from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from ..models import ClimateFinanceData, ClimateProject, FundingSource
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django_tables2 import SingleTableView, RequestConfig
from ..tables import ClimateFinanceTable
from django.db.models import Q
from django.http import HttpResponse
from ..forms.finance_form import DataImportForm, ClimateFinanceDataForm  
from django.contrib import messages
import csv
import pandas as pd
import json
from decimal import Decimal
from django.db import IntegrityError

# ----------------- LIST DATA -----------------
class ClimateFinanceDataListView(SingleTableView):
    model = ClimateFinanceData
    table_class = ClimateFinanceTable
    template_name = "pages/data_list.html"
    paginate_by = 5  

    def get_queryset(self):
        query = self.request.GET.get('q')
        qs = ClimateFinanceData.objects.all().select_related('project', 'funding_source')

        if query:
            qs = qs.filter(
                Q(project__name__icontains=query) |
                Q(funding_source__name__icontains=query) |
                Q(total_amount__icontains=query)
            )
        return qs

# ----------------- CREATE, UPDATE, DELETE -----------------
class ClimateFinanceDataCreateView(LoginRequiredMixin, CreateView):
    model = ClimateFinanceData
    form_class = ClimateFinanceDataForm
    template_name = "pages/data_form.html"
    success_url = reverse_lazy('data_list')

class ClimateFinanceDataUpdateView(LoginRequiredMixin, UpdateView):
    model = ClimateFinanceData
    form_class = ClimateFinanceDataForm
    template_name = "pages/data_edit.html"
    success_url = reverse_lazy('data_list')

class ClimateFinanceDataDeleteView(LoginRequiredMixin, DeleteView):
    model = ClimateFinanceData
    template_name = "pages/data_delete.html"
    success_url = reverse_lazy('data_list')

# ----------------- EXPORT DATA TO CSV -----------------
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="climate_finance_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Project', 'Funding Source', 'Funding Type', 'Amount', 'Currency', 'Status', 'Created At'])

    for data in ClimateFinanceData.objects.all().select_related('project', 'funding_source'):
        writer.writerow([
            data.project.name,
            data.funding_source.name,
            data.funding_type,
            data.total_amount,
            data.currency,
            data.status,
            data.created_at
        ])

    return response

# ----------------- DOWNLOAD SAMPLE FILE -----------------
def download_sample(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample_climate_finance.csv"'

    writer = csv.writer(response)
    writer.writerow(["Project", "Funding Source", "Funding Type", "Amount", "Currency", "Status"])
    writer.writerow(["Solar Project", "World Bank", "grant", "1000000", "USD", "approved"])
    writer.writerow(["Water Initiative", "UNDP", "loan", "750000", "KES", "pending"])
    return response

# ----------------- IMPORT DATA -----------------
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
    decoded_file = file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(decoded_file)
    imported_data = []
    duplicates = []

    for row in reader:
        try:
            project_name = row["Project"].strip()
            funding_source_name = row["Funding Source"].strip()
            funding_type = row["Funding Type"].strip()
            total_amount = Decimal(row["Amount"].strip())
            currency = row.get("Currency", "KES").strip()
            status = row.get("Status", "pending").strip()

            project = ClimateProject.objects.get(name__iexact=project_name)
            funding_source = FundingSource.objects.get(name__iexact=funding_source_name)

            if not ClimateFinanceData.objects.filter(
                project=project,
                funding_source=funding_source,
                funding_type=funding_type
            ).exists():
                imported_data.append(ClimateFinanceData(
                    project=project,
                    funding_source=funding_source,
                    funding_type=funding_type,
                    total_amount=total_amount,
                    currency=currency,
                    status=status
                ))
            else:
                duplicates.append(row)
        except Exception:
            continue

    ClimateFinanceData.objects.bulk_create(imported_data)
    return imported_data, duplicates

def handle_excel(file):
    df = pd.read_excel(file)
    imported_data = []
    duplicates = []

    for _, row in df.iterrows():
        try:
            project_name = str(row["Project"]).strip()
            funding_source_name = str(row["Funding Source"]).strip()
            funding_type = str(row["Funding Type"]).strip()
            total_amount = Decimal(str(row["Amount"]).strip())
            currency = str(row.get("Currency", "KES")).strip()
            status = str(row.get("Status", "pending")).strip()

            project = ClimateProject.objects.get(name__iexact=project_name)
            funding_source = FundingSource.objects.get(name__iexact=funding_source_name)

            if not ClimateFinanceData.objects.filter(
                project=project,
                funding_source=funding_source,
                funding_type=funding_type
            ).exists():
                imported_data.append(ClimateFinanceData(
                    project=project,
                    funding_source=funding_source,
                    funding_type=funding_type,
                    total_amount=total_amount,
                    currency=currency,
                    status=status
                ))
            else:
                duplicates.append(row.to_dict())
        except Exception:
            continue

    ClimateFinanceData.objects.bulk_create(imported_data)
    return imported_data, duplicates

def handle_json(file):
    data = json.load(file)
    imported_data = []
    duplicates = []

    for row in data:
        try:
            project_name = row["Project"].strip()
            funding_source_name = row["Funding Source"].strip()
            funding_type = row["Funding Type"].strip()
            total_amount = Decimal(row["Amount"])
            currency = row.get("Currency", "KES").strip()
            status = row.get("Status", "pending").strip()

            project = ClimateProject.objects.get(name__iexact=project_name)
            funding_source = FundingSource.objects.get(name__iexact=funding_source_name)

            if not ClimateFinanceData.objects.filter(
                project=project,
                funding_source=funding_source,
                funding_type=funding_type
            ).exists():
                imported_data.append(ClimateFinanceData(
                    project=project,
                    funding_source=funding_source,
                    funding_type=funding_type,
                    total_amount=total_amount,
                    currency=currency,
                    status=status
                ))
            else:
                duplicates.append(row)
        except Exception:
            continue

    ClimateFinanceData.objects.bulk_create(imported_data)
    return imported_data, duplicates

# ----------------- MANUAL ADD DATA -----------------
def add_data(request):
    if request.method == "POST":
        form = ClimateFinanceDataForm(request.POST)
        if form.is_valid():
            try:
                # Manual duplicate check
                cd = form.cleaned_data
                if ClimateFinanceData.objects.filter(
                    project=cd['project'],
                    funding_source=cd['funding_source'],
                    funding_type=cd['funding_type']
                ).exists():
                    messages.error(request, "This record already exists!")
                    return redirect('data_create')
                
                form.save()
                messages.success(request, "Data saved successfully!")
                return redirect('data_list')
            except IntegrityError:
                messages.error(request, "Database error occurred!")
                return redirect('data_create')
    else:
        form = ClimateFinanceDataForm()
    
    return render(request, 'data_create.html', {'form': form})

# ----------------- REPORTS VIEW -----------------
def reports_view(request):
    data = ClimateFinanceData.objects.all()
    
    funding_sources = list(data.values_list('funding_source__name', flat=True))
    funding_amounts = [float(amount) for amount in data.values_list('total_amount', flat=True)]
    
    project_names = list(data.values_list('project__name', flat=True))
    project_funding = [float(amount) for amount in data.values_list('total_amount', flat=True)]

    context = {
        "funding_sources": json.dumps(funding_sources),
        "funding_amounts": json.dumps(funding_amounts),
        "project_names": json.dumps(project_names),
        "project_funding": json.dumps(project_funding),
    }

    return render(request, "pages/reports.html", context)