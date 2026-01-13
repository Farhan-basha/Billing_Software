from django.db import models

# Create your models here.
"""
Customer management models
Stores customer information and billing details
"""

from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class Customer(models.Model):
    """
    Customer model for storing client information
    """
    
    customer_name = models.CharField(
        max_length=255,
        verbose_name='Customer Name',
        db_index=True
    )
    
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        verbose_name='Phone Number',
        db_index=True
    )
    
    email = models.EmailField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Email Address'
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Address'
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='City'
    )
    
    state = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='State'
    )
    
    pincode = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='PIN Code'
    )
    
    gstin = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='GSTIN',
        help_text='GST Identification Number'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Status'
    )
    
    total_invoices = models.IntegerField(
        default=0,
        verbose_name='Total Invoices',
        help_text='Total number of invoices generated for this customer'
    )
    
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name='Total Amount',
        help_text='Total billing amount across all invoices'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notes'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    
    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['-created_at']
        db_table = 'customers'
        indexes = [
            models.Index(fields=['customer_name']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.customer_name} - {self.phone_number}"
    
    def update_totals(self):
        """
        Update total invoices and amount from related invoices
        """
        from invoices.models import Invoice
        
        invoices = Invoice.objects.filter(customer=self)
        self.total_invoices = invoices.count()
        self.total_amount = sum(invoice.grand_total for invoice in invoices)
        self.save(update_fields=['total_invoices', 'total_amount', 'updated_at'])
    
    def get_full_address(self):
        """
        Return complete formatted address
        """
        address_parts = []
        
        if self.address:
            address_parts.append(self.address)
        if self.city:
            address_parts.append(self.city)
        if self.state:
            address_parts.append(self.state)
        if self.pincode:
            address_parts.append(f"PIN: {self.pincode}")
        
        return ", ".join(address_parts) if address_parts else "No address provided"