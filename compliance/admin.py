# compliance/admin.py
from django.contrib import admin
from .models import IDP, Requisition, Specification

@admin.register(IDP)
class IDPAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'budget_code', 'approved_amount', 'fiscal_year')
    search_fields = ('project_name', 'budget_code')

@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ('requisition_number', 'idp', 'estimated_cost', 'status')
    list_filter = ('status', 'date_requested')
    search_fields = ('requisition_number',)

@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('spec_number', 'requisition', 'date_drafted')
    readonly_fields = ('rigged_keywords_found',)