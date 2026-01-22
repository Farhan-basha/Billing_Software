from django.contrib import admin

# Register your models here.
"""
Admin configuration for Settings app
"""
from .models import CompanySettings


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for CompanySettings model.
    Enforces singleton pattern - only one settings record can exist.
    """
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'company_address', 'phone_number', 'email', 'website', 'gstin', 'logo')
        }),
        ('Tax Settings', {
            'fields': ('default_tax_rate', 'tax_label')
        }),
        ('Invoice Settings', {
            'fields': ('invoice_prefix', 'invoice_start_number', 'invoice_terms', 'invoice_footer')
        }),
        ('Payment Settings', {
            'fields': ('payment_due_days',)
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'account_number', 'ifsc_code'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        """
        Only allow one settings instance.
        Prevent adding new settings if one already exists.
        """
        return CompanySettings.objects.count() == 0
    
    def has_delete_permission(self, request, obj=None):
        """
        Don't allow deletion of settings.
        Settings should be updated, not deleted.
        """
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow changing settings"""
        return True

