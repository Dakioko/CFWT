# pages/urls.py
from django.urls import path
from .views import export_csv, import_data, download_sample  # Import the new view
from .views import reports_view
from .views import HomePageView, ClimateFinanceDataListView, ClimateFinanceDataCreateView, ClimateFinanceDataUpdateView, ClimateFinanceDeleteView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),  # Default home page

    path('data/', ClimateFinanceDataListView.as_view(), name='data_list'),
    path('data/add/', ClimateFinanceDataCreateView.as_view(), name='data_create'),
    path('data/edit/<int:pk>/', ClimateFinanceDataUpdateView.as_view(), name='data_update'),
    path('data/<int:pk>/delete/', ClimateFinanceDeleteView.as_view(), name='data_delete'),
    path('data/export/csv/', export_csv, name='export_csv'),
    path("data/import/", import_data, name="data_import"),
    path('import/sample/', download_sample, name='download_sample'),  # ✅ Add this line
    path('reports/', reports_view, name='reports'),
]
