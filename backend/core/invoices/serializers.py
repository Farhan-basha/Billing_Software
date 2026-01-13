"""
Invoice serializers with comprehensive validation and calculations
"""

from rest_framework import serializers
from decimal import Decimal
from .models import Invoice, InvoiceItem
from customers.models import Customer
from customers.serializers import CustomerSerializer


class InvoiceItemSerializer(serializers.ModelSerializer):
    """
    Serializer for invoice items with auto-calculation
    """
    
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'item_name', 'description', 'unit',
            'quantity', 'rate', 'total', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total', 'created_at', 'updated_at']
    
    def validate_quantity(self, value):
        """
        Ensure quantity is positive
        """
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than zero')
        return value
    
    def validate_rate(self, value):
        """
        Ensure rate is non-negative
        """
        if value < 0:
            raise serializers.ValidationError('Rate cannot be negative')
        return value


class InvoiceItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating invoice items
    """
    
    class Meta:
        model = InvoiceItem
        fields = [
            'item_name', 'description', 'unit',
            'quantity', 'rate', 'order'
        ]
    
    def validate(self, attrs):
        """
        Validate item data
        """
        quantity = attrs.get('quantity')
        rate = attrs.get('rate')
        
        if quantity and rate:
            if quantity <= 0:
                raise serializers.ValidationError({
                    'quantity': 'Quantity must be greater than zero'
                })
            if rate < 0:
                raise serializers.ValidationError({
                    'rate': 'Rate cannot be negative'
                })
        
        return attrs


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Complete invoice serializer with items and calculations
    """
    items = InvoiceItemSerializer(many=True, read_only=True)
    customer_details = CustomerSerializer(source='customer', read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'customer', 'customer_details',
            'customer_name', 'customer_phone', 'invoice_date',
            'due_date', 'status', 'subtotal', 'tax_rate',
            'tax_amount', 'discount_amount', 'grand_total',
            'notes', 'terms_and_conditions', 'items',
            'item_count', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'customer_name', 'customer_phone',
            'subtotal', 'tax_amount', 'grand_total',
            'created_by', 'created_at', 'updated_at'
        ]
    
    def get_item_count(self, obj):
        """
        Get total number of items
        """
        return obj.get_item_count()
    
    def validate_customer(self, value):
        """
        Validate customer is active
        """
        if not value.is_active:
            raise serializers.ValidationError(
                'Cannot create invoice for inactive customer'
            )
        return value
    
    def validate_discount_amount(self, value):
        """
        Ensure discount is non-negative
        """
        if value < 0:
            raise serializers.ValidationError('Discount cannot be negative')
        return value
    
    def validate_tax_rate(self, value):
        """
        Validate tax rate is within acceptable range
        """
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                'Tax rate must be between 0 and 100'
            )
        return value


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new invoices with items
    """
    items = InvoiceItemCreateSerializer(many=True, required=True)
    
    class Meta:
        model = Invoice
        fields = [
            'customer', 'invoice_date', 'due_date',
            'tax_rate', 'discount_amount', 'notes',
            'terms_and_conditions', 'items'
        ]
    
    def validate_items(self, value):
        """
        Ensure at least one item is provided
        """
        if not value:
            raise serializers.ValidationError(
                'Invoice must have at least one item'
            )
        return value
    
    def validate(self, attrs):
        """
        Validate invoice data
        """
        customer = attrs.get('customer')
        
        if customer and not customer.is_active:
            raise serializers.ValidationError({
                'customer': 'Cannot create invoice for inactive customer'
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Create invoice with items in transaction
        """
        items_data = validated_data.pop('items')
        
        # Get current user from context
        user = self.context['request'].user
        validated_data['created_by'] = user
        
        # Create invoice
        invoice = Invoice.objects.create(**validated_data)
        
        # Create items
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        # Calculate totals
        invoice.calculate_totals()
        
        # Update customer totals
        invoice.customer.update_totals()
        
        return invoice


class InvoiceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing invoices
    """
    items = InvoiceItemCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Invoice
        fields = [
            'invoice_date', 'due_date', 'status',
            'tax_rate', 'discount_amount', 'notes',
            'terms_and_conditions', 'items'
        ]
    
    def update(self, instance, validated_data):
        """
        Update invoice and optionally replace items
        """
        items_data = validated_data.pop('items', None)
        
        # Update invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # If items provided, replace existing items
        if items_data is not None:
            # Delete existing items
            instance.items.all().delete()
            
            # Create new items
            for item_data in items_data:
                InvoiceItem.objects.create(invoice=instance, **item_data)
        
        # Recalculate totals
        instance.calculate_totals()
        
        # Update customer totals
        instance.customer.update_totals()
        
        return instance


class InvoiceListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for invoice lists
    """
    customer_name = serializers.CharField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'customer_name',
            'invoice_date', 'status', 'grand_total',
            'item_count', 'created_at'
        ]
        read_only_fields = fields
    
    def get_item_count(self, obj):
        """
        Get item count
        """
        return obj.get_item_count()


class InvoicePrintSerializer(serializers.ModelSerializer):
    """
    Serializer for invoice printing with complete details
    """
    items = InvoiceItemSerializer(many=True, read_only=True)
    customer_details = CustomerSerializer(source='customer', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'customer_details', 'customer_name',
            'customer_phone', 'invoice_date', 'due_date',
            'subtotal', 'tax_rate', 'tax_amount',
            'discount_amount', 'grand_total', 'notes',
            'terms_and_conditions', 'items'
        ]
        read_only_fields = fields