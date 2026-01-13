from django.db import models

# Create your models here.
"""
Company settings and configuration models
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class CompanySettings(models.Model):
    """
    Company information and billing settings
    Singleton model - only one record should exist
    """
    
    company_name = models.CharField(
        max_length=255,
        default='Standard Steels & Hardware',
        verbose_name='Company Name'
    )
    
    company_address = models.TextField(
        default='123 Industrial Area, Steel City',
        verbose_name='Company Address'
    )
    
    phone_number = models.CharField(
        max_length=15,
        default='+91 12345 67890',
        verbose_name='Phone Number'
    )
    
    email = models.EmailField(
        max_length=255,
        default='info@standardsteels.com',
        verbose_name='Email Address'
    )
    
    website = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Website'
    )
    
    gstin = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='GSTIN',
        help_text='Company GST Identification Number'
    )
    
    logo = models.ImageField(
        upload_to='company/',
        null=True,
        blank=True,
        verbose_name='Company Logo'
    )
    
    # Tax settings
    default_tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('18.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ],
        verbose_name='Default Tax Rate (%)',
        help_text='Default GST/Tax rate for invoices'
    )
    
    tax_label = models.CharField(
        max_length=50,
        default='GST',
        verbose_name='Tax Label',
        help_text='Label for tax field (e.g., GST, VAT, Tax)'
    )
    
    # Invoice settings
    invoice_prefix = models.CharField(
        max_length=10,
        default='INV-',
        verbose_name='Invoice Number Prefix'
    )
    
    invoice_start_number = models.IntegerField(
        default=500000,
        verbose_name='Invoice Start Number'
    )
    
    invoice_terms = models.TextField(
        default='Terms & Conditions Apply | This is a computer generated invoice',
        verbose_name='Default Invoice Terms'
    )
    
    invoice_footer = models.TextField(
        blank=True,
        null=True,
        verbose_name='Invoice Footer Text'
    )
    
    # Payment settings
    payment_due_days = models.IntegerField(
        default=30,
        validators=[MinValueValidator(0)],
        verbose_name='Payment Due Days',
        help_text='Default number of days for payment due date'
    )
    
    # Bank details
    bank_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Bank Name'
    )
    
    account_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Account Number'
    )
    
    ifsc_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='IFSC Code'
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
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Company Settings'
        db_table = 'company_settings'
    
    def __str__(self):
        return self.company_name
    
    def save(self, *args, **kwargs):
        """
        Ensure only one settings record exists
        """
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Prevent deletion of settings
        """
        pass
    
    @classmethod
    def get_settings(cls):
        """
        Get or create company settings
        """
        settings, created = cls.objects.get_or_create(pk=1)
        return settings