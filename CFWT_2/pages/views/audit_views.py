from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from ..models import AuditLog  # Ensure AuditLog model exists

class AuditLogListView(LoginRequiredMixin, ListView):
    """
    Displays a list of audit logs.
    """
    model = AuditLog
    template_name = "audit/auditlog_list.html"  # Ensure template exists
    context_object_name = "audit_logs"
    ordering = ["-timestamp"]  # Latest logs first
    paginate_by = 20  # Adjust pagination as needed

class AuditLogDetailView(LoginRequiredMixin, DetailView):
    """
    Displays details of a single audit log entry.
    """
    model = AuditLog
    template_name = "audit/auditlog_detail.html"  # Ensure template exists
    context_object_name = "audit_log"
