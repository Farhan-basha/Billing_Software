"""
Customer serializers for API data transformation
"""

from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for customer model with validation
    """
    full_address = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'customer_name', 'phone_number', 'email',
            'address', 'city', 'state', 'pincode', 'gstin',
            'is_active', 'total_invoices', 'total_amount',
            'notes', 'full_address', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_invoices', 'total_amount', 
            'created_at', 'updated_at'
        ]
    
    def get_full_address(self, obj):
        """
        Get formatted full address
        """
        return obj.get_full_address()
    
    def validate_phone_number(self, value):
        """
        Validate phone number format
        """
        import re
        
        # Remove spaces and special characters
        clean_number = re.sub(r'[^\d+]', '', value)
        
        # Check if it's a valid format
        if not re.match(r'^\+?1?\d{9,15}$', clean_number):
            raise serializers.ValidationError(
                'Phone number must be 9-15 digits. Format: +999999999'
            )
        
        return value
    
    def validate_email(self, value):
        """
        Validate email is unique if provided
        """
        if value:
            instance = self.instance
            qs = Customer.objects.filter(email=value)
            
            if instance:
                qs = qs.exclude(pk=instance.pk)
            
            if qs.exists():
                raise serializers.ValidationError(
                    'A customer with this email already exists'
                )
        
        return value


class CustomerListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for customer lists
    """
    
    class Meta:
        model = Customer
        fields = [
            'id', 'customer_name', 'phone_number', 
            'email', 'total_invoices', 'total_amount',
            'is_active', 'created_at'
        ]
        read_only_fields = fields


class CustomerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new customers
    """
    
    class Meta:
        model = Customer
        fields = [
            'customer_name', 'phone_number', 'email',
            'address', 'city', 'state', 'pincode', 
            'gstin', 'notes'
        ]
    
    def create(self, validated_data):
        """
        Create customer with validation
        """
        return Customer.objects.create(**validated_data)


class CustomerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating customer information
    """
    
    class Meta:
        model = Customer
        fields = [
            'customer_name', 'phone_number', 'email',
            'address', 'city', 'state', 'pincode',
            'gstin', 'is_active', 'notes'
        ]
    
    def update(self, instance, validated_data):
        """
        Update customer with validation
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance