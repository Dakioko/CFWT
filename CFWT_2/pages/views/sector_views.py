# Django Imports
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_tables2 import SingleTableView, RequestConfig
from ..tables import SectorTable
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import csv
import pandas as pd

# Local Imports
from ..models import Sector
from ..forms.sector_form import SectorForm

# Sector List View
class SectorListView(SingleTableView):
    model = Sector
    template_name = "sector/sector_list.html"
    table_class = SectorTable
    context_object_name = "sectors"
    paginate_by = 10  # Pagination for better UI experience
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()  # Get and clean search query
        qs = Sector.objects.all()  # Get all Sector records

        if query:
            qs = qs.filter(
                Q(name__icontains=query) |  # Search by sector name
                Q(description__icontains=query)  # Search by sector description
        )

        return qs
    
    
    
    

# Sector Detail View
class SectorDetailView(LoginRequiredMixin, DetailView):
    model = Sector
    template_name = "sector/sector_detail.html"
    context_object_name = "sector"

# Sector Create View
class SectorCreateView(LoginRequiredMixin, CreateView):
    model = Sector
    form_class = SectorForm
    template_name = "sector/sector_form.html"
    success_url = reverse_lazy("sector_list")

# Sector Update View
class SectorUpdateView(LoginRequiredMixin, UpdateView):
    model = Sector
    form_class = SectorForm
    template_name = "sector/sector_edit.html"
    success_url = reverse_lazy("sector_list")

# Sector Delete View
class SectorDeleteView(LoginRequiredMixin, DeleteView):
    model = Sector
    template_name = "sector/sector_delete.html"
    success_url = reverse_lazy("sector_list")

# ----------------- EXPORT SECTOR DATA TO CSV -----------------
def export_csv_sectors(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Sectors.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Description'])

    for sector in Sector.objects.all():
        writer.writerow([
            sector.name,
            sector.description or ""
        ])

    return response