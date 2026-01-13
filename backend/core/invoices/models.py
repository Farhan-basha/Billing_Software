from django.db import models

# Create your models here.
"""
Invoice management models
Core billing functionality with items and calculations
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from customers.models import Customer


class Invoice(models.Model):
    """
    Main invoice model with comprehensive billing details
    """
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name='Invoice Number'
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Customer'
    )
    
    customer_name = models.CharField(
        max_length=255,
        verbose_name='Customer Name',
        help_text='Cached customer name for historical records'
    )
    
    customer_phone = models.CharField(
        max_length=15,
        verbose_name='Customer Phone',
        help_text='Cached customer phone for historical records'
    )
    
    invoice_date = models.DateField(
        default=timezone.now,
        verbose_name='Invoice Date',
        db_index=True
    )
    
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Due Date'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True,
        verbose_name='Status'
    )
    
    # Calculation fields
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Subtotal'
    )
    
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Tax Rate (%)',
        help_text='Tax percentage (e.g., 18.00 for 18%)'
    )
    
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Tax Amount'
    )
    
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Discount Amount'
    )
    
    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Grand Total'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notes'
    )
    
    terms_and_conditions = models.TextField(
        blank=True,
        null=True,
        verbose_name='Terms and Conditions'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices',
        verbose_name='Created By'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
        db_index=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    
    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-created_at']
        db_table = 'invoices'
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['invoice_date']),
            models.Index(fields=['status']),
            models.Index(fields=['customer', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to cache customer details and generate invoice number
        """
        # Cache customer details for historical accuracy
        if self.customer:
            self.customer_name = self.customer.customer_name
            self.customer_phone = self.customer.phone_number
        
        # Generate invoice number if not exists
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_invoice_number():
        """
        Generate unique invoice number with prefix
        """
        from django.conf import settings
        
        prefix = getattr(settings, 'INVOICE_NUMBER_PREFIX', 'INV-')
        start_number = getattr(settings, 'INVOICE_NUMBER_START', 500000)
        
        last_invoice = Invoice.objects.order_by('-id').first()
        
        if last_invoice and last_invoice.invoice_number.startswith(prefix):
            try:
                last_number = int(last_invoice.invoice_number.replace(prefix, ''))
                new_number = last_number + 1
            except ValueError:
                new_number = start_number
        else:
            new_number = start_number
        
        return f"{prefix}{new_number}"
    
    def calculate_totals(self):
        """
        Calculate all invoice totals based on items
        """
        # Calculate subtotal from items
        items = self.items.all()
        self.subtotal = sum(item.total for item in items)
        
        # Calculate tax
        if self.tax_rate > 0:
            self.tax_amount = (self.subtotal * self.tax_rate) / Decimal('100.00')
        else:
            self.tax_amount = Decimal('0.00')
        
        # Calculate grand total
        self.grand_total = self.subtotal + self.tax_amount - self.discount_amount
        
        # Ensure grand total is not negative
        if self.grand_total < 0:
            self.grand_total = Decimal('0.00')
        
        self.save(update_fields=['subtotal', 'tax_amount', 'grand_total', 'updated_at'])
    
    def get_item_count(self):
        """
        Return total number of items in invoice
        """
        return self.items.count()
    
    def mark_as_sent(self):
        """
        Mark invoice as sent
        """
        self.status = 'sent'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_paid(self):
        """
        Mark invoice as paid
        """
        self.status = 'paid'
        self.save(update_fields=['status', 'updated_at'])
    
    def cancel(self):
        """
        Cancel the invoice
        """
        self.status = 'cancelled'
        self.save(update_fields=['status', 'updated_at'])


class InvoiceItem(models.Model):
    """
    Individual items within an invoice
    """
    
    UNIT_CHOICES = (
        ('piece', 'Piece'),
        ('sq meter', 'Square Meter'),
        ('meter', 'Meter'),
        ('kg', 'Kilogram'),
        ('ton', 'Ton'),
        ('box', 'Box'),
        ('set', 'Set'),
    )
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Invoice'
    )
    
    item_name = models.CharField(
        max_length=255,
        verbose_name='Item Name'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description'
    )
    
    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default='piece',
        verbose_name='Unit'
    )
    
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Quantity'
    )
    
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Rate'
    )
    
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Total'
    )
    
    order = models.IntegerField(
        default=0,
        verbose_name='Order',
        help_text='Display order of items'
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
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'
        ordering = ['order', 'id']
        db_table = 'invoice_items'
        indexes = [
            models.Index(fields=['invoice', 'order']),
        ]
    
    def __str__(self):
        return f"{self.item_name} - {self.quantity} {self.unit}"
    
    def save(self, *args, **kwargs):
        """
        Calculate total before saving
        """
        self.total = self.quantity * self.rate
        super().save(*args, **kwargs)
        
        # Recalculate invoice totals
        self.invoice.calculate_totals()
    
    def delete(self, *args, **kwargs):
        """
        Recalculate invoice totals after deletion
        """
        invoice = self.invoice
        super().delete(*args, **kwargs)
        invoice.calculate_totals()