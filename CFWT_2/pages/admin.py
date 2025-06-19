from django.contrib import admin
from .models import (
    Sector, FundingSource, Recipient, ClimateProject, 
    ClimateFinanceData, Disbursement, AuditLog
)

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(FundingSource)
class FundingSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'country', 'contact_email', 'website', 'created_at')
    search_fields = ('name', 'country')
    list_filter = ('type', 'country')
    ordering = ('-created_at',)

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'location', 'contact_email', 'created_at')
    search_fields = ('name', 'location')
    list_filter = ('type', 'location')
    ordering = ('-created_at',)

@admin.register(ClimateProject)
class ClimateProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'recipient', 'sector', 'start_date', 'end_date', 'created_at')
    search_fields = ('name', 'recipient__name', 'sector__name')
    list_filter = ('sector',)
    ordering = ('-created_at',)

@admin.register(ClimateFinanceData)
class ClimateFinanceDataAdmin(admin.ModelAdmin):
    list_display = ('project', 'funding_source', 'funding_type', 'total_amount', 'currency', 'status', 'created_at')
    search_fields = ('project__name', 'funding_source__name', 'funding_type')
    list_filter = ('funding_type', 'currency', 'status')
    ordering = ('-created_at',)

@admin.register(Disbursement)
class DisbursementAdmin(admin.ModelAdmin):
    list_display = ('finance_data', 'amount', 'currency', 'disbursement_date', 'notes')
    search_fields = ('finance_data__project__name',)
    list_filter = ('currency',)
    ordering = ('-disbursement_date',)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('finance_data', 'action', 'performed_by', 'timestamp', 'details')
    search_fields = ('finance_data__project__name', 'performed_by')
    list_filter = ('action',)
    ordering = ('-timestamp',)
