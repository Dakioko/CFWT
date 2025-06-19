# Django Imports
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_tables2.views import SingleTableView
from django.db.models import Q
import logging
from django.http import HttpResponse
from django.contrib import messages
import csv, json, pandas as pd
from decimal import Decimal
from django.shortcuts import render, redirect

# Local Imports
from ..models import Recipient
from ..forms.recipient_form import RecipientForm, DataImportForm
from ..tables import RecipientTable

# Recipient List View
class RecipientListView(SingleTableView):
    model = Recipient
    template_name = "recipient/recipient_list.html"
    table_class = RecipientTable
    context_object_name = "recipients"
    paginate_by = 10  # Pagination for better UI experience
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()  # Get and clean search query
        qs = Recipient.objects.all()  # Get all Recipient records

        if query:
            qs = qs.filter(
                Q(name__icontains=query) |  # Search by recipient name
                Q(type__icontains=query) |  # Search by type (government, NGO, etc.)
                Q(location__icontains=query) |  # Search by location
                Q(contact_email__icontains=query)  # Search by email
            )

        return qs

# Recipient Detail View
class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = "recipient/recipient_detail.html"
    context_object_name = "recipient"

# Recipient Create View
class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "recipient/recipient_form.html"
    success_url = reverse_lazy("recipient_list")

# Recipient Update View
class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "recipient/recipient_edit.html"
    success_url = reverse_lazy("recipient_list")

# Recipient Delete View
class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = "recipient/recipient_delete.html"
    success_url = reverse_lazy("recipient_list")
    
    def post(self, request, *args, **kwargs):
        recipient = self.get_object()
        # Consider changing to info for production
        logging.info(f"Deleting recipient: {recipient.pk}")
        return super().post(request, *args, **kwargs)

# ----------------- EXPORT RECIPIENT DATA TO CSV -----------------
def export_csv_recipients(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Recipients.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Type', 'Location', 'Contact Email', 'Created At'
    ])

    for recipient in Recipient.objects.all():
        writer.writerow([
            recipient.name,
            recipient.get_type_display(),  # Human-readable type
            recipient.location,
            recipient.contact_email or "",
            recipient.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response

# ----------------- IMPORT DATA (CSV, XLSX, JSON) -----------------
# ----------------- IMPORT DATA (CSV, XLSX, JSON) -----------------
def import_recipients(request):
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


# ----------------- HELPER FUNCTIONS FOR RECIPIENT -----------------
def handle_csv(file):
    """Handle CSV file import for Recipient model and check for duplicates."""
    decoded_file = file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(decoded_file)

    imported_data = []
    duplicates = []

    for row in reader:
        name = row["Name"].strip().lower()
        type_ = row["Type"].strip().lower()
        location = row["Location"].strip().lower()
        contact_email = row.get("Contact Email", "").strip().lower() or None

        filters = {
            "name__iexact": name,
            "type__iexact": type_,
            "location__iexact": location,
        }
        if contact_email:
            filters["contact_email__iexact"] = contact_email
        else:
            filters["contact_email__isnull"] = True

        if not Recipient.objects.filter(**filters).exists():
            imported_data.append(Recipient(
                name=name,
                type=type_,
                location=location,
                contact_email=contact_email
            ))
        else:
            duplicates.append(row)

    Recipient.objects.bulk_create(imported_data)
    return imported_data, duplicates


def handle_excel(file):
    """Handle Excel (XLSX) file import for Recipient model and check for duplicates."""
    df = pd.read_excel(file)
    imported_data = []
    duplicates = []

    for _, row in df.iterrows():
        name = str(row["Name"]).strip().lower()
        type_ = str(row["Type"]).strip().lower()
        location = str(row["Location"]).strip().lower()
        contact_email = str(row.get("Contact Email", "")).strip().lower() or None

        filters = {
            "name__iexact": name,
            "type__iexact": type_,
            "location__iexact": location,
        }
        if contact_email:
            filters["contact_email__iexact"] = contact_email
        else:
            filters["contact_email__isnull"] = True

        if not Recipient.objects.filter(**filters).exists():
            imported_data.append(Recipient(
                name=name,
                type=type_,
                location=location,
                contact_email=contact_email
            ))
        else:
            duplicates.append(row)

    Recipient.objects.bulk_create(imported_data)
    return imported_data, duplicates


def handle_json(file):
    """Handle JSON file import for Recipient model and check for duplicates."""
    data = json.load(file)
    imported_data = []
    duplicates = []

    for row in data:
        name = row["Name"].strip().lower()
        type_ = row["Type"].strip().lower()
        location = row["Location"].strip().lower()
        contact_email = row.get("Contact Email", "").strip().lower() or None

        filters = {
            "name__iexact": name,
            "type__iexact": type_,
            "location__iexact": location,
        }
        if contact_email:
            filters["contact_email__iexact"] = contact_email
        else:
            filters["contact_email__isnull"] = True

        if not Recipient.objects.filter(**filters).exists():
            imported_data.append(Recipient(
                name=name,
                type=type_,
                location=location,
                contact_email=contact_email
            ))
        else:
            duplicates.append(row)

    Recipient.objects.bulk_create(imported_data)
    return imported_data, duplicates

def download_sample_recipients(request):
    """Generate and return a sample CSV file for Recipient data."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample_recipients.csv"'

    writer = csv.writer(response)
    writer.writerow(["Name", "Type", "Location", "Contact Email"])  # Column headers
    writer.writerow(["GreenFuture Initiative", "ngo", "Nairobi", "kenya@greenfuture.org"])
    writer.writerow(["Clean Energy Fund", "government", "Accra", "contact@cef.gov"])
    writer.writerow(["EcoVillage Cooperative", "community", "Lilongwe", "info@ecovillage.org"])
    writer.writerow(["SustainableTech Inc", "private", "Lagos", "hello@sustech.com"])

    return response