"""
Complete Admin Configuration for all models
Copy these to respective admin.py files in each app
"""

# ============================================================
# backend/customers/admin.py
# ============================================================

from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'phone_number', 'email', 'total_invoices', 'total_amount', 'is_active', 'created_at']
    list_filter = ['is_active', 'city', 'state', 'created_at']
    search_fields = ['customer_name', 'phone_number', 'email']
    readonly_fields = ['total_invoices', 'total_amount', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer_name', 'phone_number', 'email')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'pincode')
        }),
        ('Business Details', {
            'fields': ('gstin', 'is_active')
        }),
        ('Statistics', {
            'fields': ('total_invoices', 'total_amount'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ============================================================
# backend/invoices/admin.py
# ============================================================

from django.contrib import admin
from .models import Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['item_name', 'unit', 'quantity', 'rate', 'total']
    readonly_fields = ['total']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer_name', 'invoice_date', 'status', 'grand_total', 'created_at']
    list_filter = ['status', 'invoice_date', 'created_at']
    search_fields = ['invoice_number', 'customer_name', 'customer_phone']
    readonly_fields = ['invoice_number', 'customer_name', 'customer_phone', 'subtotal', 'tax_amount', 'grand_total', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'customer', 'customer_name', 'customer_phone')
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Calculations', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount_amount', 'grand_total')
        }),
        ('Additional Information', {
            'fields': ('notes', 'terms_and_conditions'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'item_name', 'unit', 'quantity', 'rate', 'total']
    list_filter = ['unit', 'invoice__invoice_date']
    search_fields = ['item_name', 'invoice__invoice_number']
    readonly_fields = ['total']


# ============================================================
# backend/settings_app/admin.py
# ============================================================

from django.contrib import admin
from .models import CompanySettings

@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
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
        # Only allow one settings instance
        return CompanySettings.objects.count() == 0
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False