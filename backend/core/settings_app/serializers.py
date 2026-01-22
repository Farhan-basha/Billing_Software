"""
Serializers for Company Settings app
"""
from rest_framework import serializers
from .models import CompanySettings


class CompanySettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for CompanySettings model
    Handles all company configuration and invoice settings
    """
    
    class Meta:
        model = CompanySettings
        fields = [
            'id',
            'company_name',
            'company_address',
            'phone_number',
            'email',
            'website',
            'gstin',
            'logo',
            'default_tax_rate',
            'tax_label',
            'invoice_prefix',
            'invoice_start_number',
            'invoice_terms',
            'invoice_footer',
            'payment_due_days',
            'bank_name',
            'account_number',
            'ifsc_code',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_default_tax_rate(self, value):
        """
        Validate tax rate is between 0 and 100
        """
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Tax rate must be between 0 and 100."
            )
        return value
    
    def validate_invoice_start_number(self, value):
        """
        Validate invoice start number is positive
        """
        if value < 0:
            raise serializers.ValidationError(
                "Invoice start number must be positive."
            )
        return value
    
    def validate_payment_due_days(self, value):
        """
        Validate payment due days is positive
        """
        if value and value < 0:
            raise serializers.ValidationError(
                "Payment due days must be positive."
            )
        return value
