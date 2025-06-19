from django.urls import path
from .views.general import DashboardView
from .views.sector_views import SectorListView,SectorCreateView, SectorUpdateView, SectorDeleteView
from .views.funding_views import FundingSourceListView,  FundingSourceCreateView, FundingSourceUpdateView, FundingSourceDeleteView, import_funding_sources, download_funding_source_sample
from .views.recipient_views import RecipientListView,  RecipientCreateView, RecipientUpdateView, RecipientDeleteView
from .views.project_views import ClimateProjectListView,  ClimateProjectCreateView, ClimateProjectUpdateView, ClimateProjectDeleteView
from .views.finance_views import ClimateFinanceDataListView, ClimateFinanceDataCreateView, ClimateFinanceDataUpdateView, ClimateFinanceDataDeleteView
from .views.disbursement_views import DisbursementListView, DisbursementCreateView, DisbursementUpdateView, DisbursementDeleteView
from .views.audit_views import AuditLogListView, AuditLogDetailView
from .views.finance_views import export_csv, import_data, download_sample  # Import the new view
from .views.disbursement_views import export_csv_dis
from .views.project_views import export_csv_projects
from .views.funding_views import export_csv_funding_sources
from .views.sector_views import export_csv_sectors
from .views.recipient_views import export_csv_recipients, import_recipients, download_sample_recipients

urlpatterns = [
    # 📌 General
     path("", DashboardView.as_view(), name="dashboard"),

    # 📌 Sector URLs
    path("sectors/", SectorListView.as_view(), name="sector_list"),
    path("sectors/add/", SectorCreateView.as_view(), name="sector_create"),
    path("sectors/edit/<int:pk>/", SectorUpdateView.as_view(), name="sector_update"),
    path("sectors/<int:pk>/delete/", SectorDeleteView.as_view(), name="sector_delete"),
    path('sectors/export/csv/', export_csv_sectors, name='export_csv_sectors'),

    # 📌 Funding Source URLs
    path("funding/", FundingSourceListView.as_view(), name="funding_list"),
    path("funding/add/", FundingSourceCreateView.as_view(), name="funding_create"),
    path("funding/edit/<int:pk>/", FundingSourceUpdateView.as_view(), name="fundingsource_update"),
    path("funding/<int:pk>/delete/", FundingSourceDeleteView.as_view(), name="fundingsource_delete"),
    path('funding/export/csv/', export_csv_funding_sources, name='export_csv_funding_sources'),
    path("funding/import/", import_funding_sources, name="import_funding_sources"),
    path('funding/sample/', download_funding_source_sample, name='download_funding_sample'),  # ✅ Add this line
    

    # 📌 Recipient URLs
    path("recipients/", RecipientListView.as_view(), name="recipient_list"),
    path("recipients/add/", RecipientCreateView.as_view(), name="recipient_create"),
    path("recipients/edit/<int:pk>/", RecipientUpdateView.as_view(), name="recipient_update"),
    path("recipients/<int:pk>/delete/", RecipientDeleteView.as_view(), name="recipient_delete"),
    path('recipients/export/csv/', export_csv_recipients, name='export_csv_recipients'),
    path("recipients/import/", import_recipients, name="import_recipients"),
    path('recipients/sample/', download_sample_recipients, name='download_sample_recipients'),  # ✅ Add this line

    # 📌 Climate Project URLs
    path("projects/", ClimateProjectListView.as_view(), name="project_list"),
    path("projects/add/", ClimateProjectCreateView.as_view(), name="project_create"),
    path("projects/edit/<int:pk>/", ClimateProjectUpdateView.as_view(), name="climateproject_update"),
    path("projects/<int:pk>/delete/", ClimateProjectDeleteView.as_view(), name="climateproject_delete"),
    path('projects/export/csv/', export_csv_projects, name='export_csv_projects'),

    # 📌 Climate Finance Data URLs
    path("finance/", ClimateFinanceDataListView.as_view(), name="data_list"),
    path("finance/add/", ClimateFinanceDataCreateView.as_view(), name="data_create"),
    path("finance/edit/<int:pk>/", ClimateFinanceDataUpdateView.as_view(), name="climatefinancedata_update"),
    path("finance/<int:pk>/delete/", ClimateFinanceDataDeleteView.as_view(), name="climatefinancedata_delete"),
    path('finance/export/csv/', export_csv, name='export_csv'),
    path("finance/import/", import_data, name="data_import"),
    path('finance/sample/', download_sample, name='download_sample'),  # ✅ Add this line


    # 📌 Disbursement URLs
    path("disbursements/", DisbursementListView.as_view(), name="disbursement_list"),
    path("disbursements/add/", DisbursementCreateView.as_view(), name="disbursement_create"),
    path("disbursements/edit/<int:pk>/", DisbursementUpdateView.as_view(), name="disbursement_update"),
    path("disbursements/<int:pk>/delete/", DisbursementDeleteView.as_view(), name="disbursement_delete"),
    path('disbursments/export/csv/', export_csv_dis, name='export_disburse'),

    # 📌 Audit Log URLs
    path("auditlogs/", AuditLogListView.as_view(), name="auditlog_list"),
    path("auditlogs/<int:pk>/", AuditLogDetailView.as_view(), name="auditlog_detail"),
]


