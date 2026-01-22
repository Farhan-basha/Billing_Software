from django.contrib import admin

# Register your models here.
"""
Admin configuration for Invoice app
"""
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    """
    Inline admin for InvoiceItem model.
    Allows editing invoice items directly within the Invoice admin page.
    """
    model = InvoiceItem
    extra = 1
    fields = ['item_name', 'unit', 'quantity', 'rate', 'total']
    readonly_fields = ['total']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    Admin interface for Invoice model.
    Provides comprehensive invoice management with item editing.
    """
    list_display = [
        'invoice_number',
        'customer_name',
        'invoice_date',
        'status',
        'grand_total',
        'created_at'
    ]
    list_filter = ['status', 'invoice_date', 'created_at']
    search_fields = ['invoice_number', 'customer_name', 'customer_phone']
    readonly_fields = [
        'invoice_number',
        'customer_name',
        'customer_phone',
        'subtotal',
        'tax_amount',
        'grand_total',
        'created_at',
        'updated_at'
    ]
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
        """Auto-set created_by field for new invoices"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """Make sensitive fields readonly"""
        if obj and not request.user.is_superuser:
            return self.readonly_fields + ['customer', 'status']
        return self.readonly_fields


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    """
    Admin interface for InvoiceItem model.
    """
    list_display = ['invoice', 'item_name', 'unit', 'quantity', 'rate', 'total']
    list_filter = ['unit', 'invoice__invoice_date']
    search_fields = ['item_name', 'invoice__invoice_number']
    readonly_fields = ['total']

    fieldsets = (
        ('Item Details', {
            'fields': ('invoice', 'item_name', 'unit')
        }),
        ('Quantity & Rate', {
            'fields': ('quantity', 'rate')
        }),
        ('Total', {
            'fields': ('total',),
            'classes': ('collapse',)
        }),
    )

