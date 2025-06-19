from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class DashboardView(TemplateView):
    """Renders the dashboard (requires login)."""
    template_name = "dashboard.html"
