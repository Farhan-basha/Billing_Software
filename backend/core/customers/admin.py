from django.contrib import admin

# Register your models here.
"""
Admin configuration for Customer app
"""
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Admin interface for Customer model.
    Displays comprehensive customer information with filtering and search capabilities.
    """
    list_display = [
        'customer_name',
        'phone_number',
        'email',
        'total_invoices',
        'total_amount',
        'is_active',
        'created_at'
    ]
    list_filter = ['is_active', 'city', 'state', 'created_at']
    search_fields = ['customer_name', 'phone_number', 'email', 'gstin']
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

    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly if not a superuser"""
        if not request.user.is_superuser and obj:
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

