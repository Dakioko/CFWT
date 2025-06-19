# Django Imports
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_tables2 import SingleTableView, RequestConfig
from ..tables import FundingSourceTable
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import csv, json
import pandas as pd
from decimal import Decimal


# Local Imports
from ..models import FundingSource
from ..forms.funding_source import FundingSourceForm, DataImportForm

# Funding Source List View
class FundingSourceListView(SingleTableView):
    model = FundingSource
    table_class = FundingSourceTable
    template_name = "funding/funding_list.html"
    context_object_name = "funding_sources"
    paginate_by = 10  # Pagination

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()  # Get and clean search query
        qs = FundingSource.objects.all()  # Get all Funding Sources

        if query:
            qs = qs.filter(
                Q(name__icontains=query) |  # Search by funding source name
                Q(type__icontains=query) |  # Search by funding type (government, NGO, etc.)
                Q(country__icontains=query)  # Search by country
            )

        return qs

# Funding Source Detail View
class FundingSourceDetailView(LoginRequiredMixin, DetailView):
    model = FundingSource
    template_name = "funding/funding_detail.html"
    context_object_name = "funding_source"

# Funding Source Create View
class FundingSourceCreateView(LoginRequiredMixin, CreateView):
    model = FundingSource
    form_class = FundingSourceForm
    template_name = "funding/funding_form.html"
    success_url = reverse_lazy("funding_list")

# Funding Source Update View
class FundingSourceUpdateView(LoginRequiredMixin, UpdateView):
    model = FundingSource
    form_class = FundingSourceForm
    template_name = "funding/funding_edit.html"
    success_url = reverse_lazy("funding_list")

# Funding Source Delete View
class FundingSourceDeleteView(LoginRequiredMixin, DeleteView):
    model = FundingSource
    template_name = "funding/funding_delete.html"
    success_url = reverse_lazy("funding_list")

# ----------------- EXPORT FUNDING SOURCE DATA TO CSV -----------------
def export_csv_funding_sources(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Funding Sources.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Type', 'Country', 'Contact Email', 'Website', 'Created At'
    ])

    for source in FundingSource.objects.all():
        writer.writerow([
            source.name,
            source.get_type_display(),  # Displays the human-readable choice label
            source.country,
            source.contact_email or "",
            source.website or "",
            source.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response

def import_funding_sources(request):
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
                    messages.warning(request, f"Skipped {len(duplicates)} duplicate or incomplete records.")

                if imported_data:
                    messages.success(request, f"Successfully imported {len(imported_data)} records.")
                else:
                    messages.info(request, "No new data was imported.")

            except Exception as e:
                messages.error(request, f"Error importing file: {str(e)}")

            return redirect("data_import")

    else:
        form = DataImportForm()
    
    return render(request, "funding/data_import.html", {"form": form})

def handle_csv(file):
    decoded_file = file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(decoded_file)

    imported_data = []
    duplicates = []

    for row in reader:
        try:
            project_name = row["Project Name"].strip()
            funding_name = row["Funding Source"].strip()
            amount = Decimal(row["Amount"].strip())
            funding_type = row.get("Funding Type", "government").strip().lower()
            country = row.get("Country", "Unknown").strip()
            contact_email = row.get("Contact Email", "").strip() or None
            website = row.get("Website", "").strip() or None

            funding_source = get_or_create_funding_source(
                name=funding_name,
                type=funding_type,
                country=country,
                contact_email=contact_email,
                website=website
            )

            if not FundingSource.objects.filter(
                project_name__iexact=project_name,
                funding_source=funding_source,
                amount=amount
            ).exists():
                imported_data.append(FundingSource(
                    project_name=project_name,
                    funding_source=funding_source,
                    amount=amount
                ))
            else:
                duplicates.append(row)

        except Exception as e:
            duplicates.append(row)

    FundingSource.objects.bulk_create(imported_data)
    return imported_data, duplicates

def handle_excel(file):
    df = pd.read_excel(file)
    imported_data = []
    duplicates = []

    for _, row in df.iterrows():
        try:
            project_name = str(row["Project Name"]).strip()
            funding_name = str(row["Funding Source"]).strip()
            amount = Decimal(str(row["Amount"]).strip())
            funding_type = str(row.get("Funding Type", "government")).strip().lower()
            country = str(row.get("Country", "Unknown")).strip()
            contact_email = str(row.get("Contact Email", "")).strip() or None
            website = str(row.get("Website", "")).strip() or None

            funding_source = get_or_create_funding_source(
                name=funding_name,
                type=funding_type,
                country=country,
                contact_email=contact_email,
                website=website
            )

            if not FundingSource.objects.filter(
                project_name__iexact=project_name,
                funding_source=funding_source,
                amount=amount
            ).exists():
                imported_data.append(FundingSource(
                    project_name=project_name,
                    funding_source=funding_source,
                    amount=amount
                ))
            else:
                duplicates.append(row.to_dict())

        except Exception as e:
            duplicates.append(row.to_dict())

    FundingSource.objects.bulk_create(imported_data)
    return imported_data, duplicates

def handle_json(file):
    data = json.load(file)
    imported_data = []
    duplicates = []

    for row in data:
        try:
            project_name = row["Project Name"].strip()
            funding_name = row["Funding Source"].strip()
            amount = Decimal(row["Amount"])
            funding_type = row.get("Funding Type", "government").strip().lower()
            country = row.get("Country", "Unknown").strip()
            contact_email = row.get("Contact Email", "").strip() or None
            website = row.get("Website", "").strip() or None

            funding_source = get_or_create_funding_source(
                name=funding_name,
                type=funding_type,
                country=country,
                contact_email=contact_email,
                website=website
            )

            if not FundingSource.objects.filter(
                project_name__iexact=project_name,
                funding_source=funding_source,
                amount=amount
            ).exists():
                imported_data.append(FundingSource(
                    project_name=project_name,
                    funding_source=funding_source,
                    amount=amount
                ))
            else:
                duplicates.append(row)

        except Exception as e:
            duplicates.append(row)

    FundingSource.objects.bulk_create(imported_data)
    return imported_data, duplicates

def get_or_create_funding_source(name, type="government", country="Unknown", contact_email=None, website=None):
    return FundingSource.objects.get_or_create(
        name__iexact=name.strip(),
        defaults={
            "name": name.strip(),
            "type": type,
            "country": country,
            "contact_email": contact_email,
            "website": website,
        }
    )[0]
def download_funding_source_sample(request):
    headers = ["Name", "Type", "Country", "Contact Email", "Website"]

    # Optional example rows
    sample_data = [
        ["Green Climate Fund", "international", "South Korea", "info@gcf.org", "https://www.greenclimate.fund"],
        ["Ministry of Environment", "government", "Kenya", "contact@environment.go.ke", "https://environment.go.ke"]
    ]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="funding_source_sample.csv"'

    writer = csv.writer(response)
    writer.writerow(headers)
    writer.writerows(sample_data)

    return response