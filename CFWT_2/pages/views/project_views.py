# Django Imports
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django_tables2 import SingleTableView
from ..tables import ClimateProjectTable
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import csv
import pandas as pd

# Local Imports
from ..models import ClimateProject
from ..forms.project_form import ClimateProjectForm

class ClimateProjectListView(SingleTableView):
    model = ClimateProject
    template_name = "project/project_list.html"  # Updated template name
    table_class = ClimateProjectTable
    context_object_name = "projects"
    paginate_by = 10  # Pagination for better UI experience

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()  # Get and clean search query
        qs = ClimateProject.objects.all()  # Fetch all projects

        if query:
            qs = qs.filter(
                Q(name__icontains=query) |  # Search by project name
                Q(description__icontains=query) |  # Search by description
                Q(recipient__name__icontains=query) |  # Search by recipient name
                Q(sector__name__icontains=query)  # Search by sector name
            )

        return qs

# Climate Project Create View
class ClimateProjectCreateView(LoginRequiredMixin, CreateView):
    model = ClimateProject
    form_class = ClimateProjectForm
    template_name = "project/project_form.html"
    success_url = reverse_lazy("project_list")

# Climate Project Update View
class ClimateProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = ClimateProject
    form_class = ClimateProjectForm
    template_name = "project/project_edit.html"
    success_url = reverse_lazy("project_list")

# Climate Project Delete View
class ClimateProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = ClimateProject
    template_name = "project/project_delete.html"
    success_url = reverse_lazy("project_list")

# ----------------- EXPORT CLIMATE PROJECT DATA TO CSV -----------------
def export_csv_projects(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Climate Projects.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Project Name', 'Description', 'Recipient', 'Sector',
        'Start Date', 'End Date', 'Created At'
    ])

    for project in ClimateProject.objects.select_related('recipient', 'sector').all():
        writer.writerow([
            project.name,
            project.description or "",
            str(project.recipient),
            str(project.sector) if project.sector else "",
            project.start_date.strftime('%Y-%m-%d'),
            project.end_date.strftime('%Y-%m-%d') if project.end_date else "",
            project.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response

