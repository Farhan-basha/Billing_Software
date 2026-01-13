from django.shortcuts import render

# Create your views here.
"""
Customer management views for CRUD operations
"""

from rest_framework import status, generics, filters, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Customer
from .serializers import (
    CustomerSerializer, CustomerListSerializer,
    CustomerCreateSerializer, CustomerUpdateSerializer
)


class CustomerListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list and create customers
    """
    queryset = Customer.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'city', 'state']
    search_fields = ['customer_name', 'phone_number', 'email']
    ordering_fields = ['customer_name', 'created_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        Use different serializers for list and create
        """
        if self.request.method == 'POST':
            return CustomerCreateSerializer
        return CustomerListSerializer
    
    def list(self, request, *args, **kwargs):
        """
        Return paginated list of customers
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'data': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        """
        Create new customer
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Customer created successfully',
            'data': CustomerSerializer(customer).data
        }, status=status.HTTP_201_CREATED)


class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, and delete customer
    """
    queryset = Customer.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Use different serializers based on method
        """
        if self.request.method in ['PUT', 'PATCH']:
            return CustomerUpdateSerializer
        return CustomerSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """
        Get customer details
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """
        Update customer information
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Customer updated successfully',
            'data': CustomerSerializer(customer).data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete customer (deactivate)
        """
        instance = self.get_object()
        
        # Check if customer has invoices
        if instance.total_invoices > 0:
            # Soft delete - deactivate instead
            instance.is_active = False
            instance.save()
            
            return Response({
                'success': True,
                'message': 'Customer deactivated successfully (has existing invoices)'
            }, status=status.HTTP_200_OK)
        
        # Hard delete if no invoices
        instance.delete()
        
        return Response({
            'success': True,
            'message': 'Customer deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class CustomerSearchView(generics.ListAPIView):
    """
    API endpoint for customer search
    """
    queryset = Customer.objects.filter(is_active=True)
    serializer_class = CustomerListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['customer_name', 'phone_number', 'email']
    
    def list(self, request, *args, **kwargs):
        """
        Search customers by name, phone, or email
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class CustomerStatsView(generics.RetrieveAPIView):
    """
    API endpoint to get customer statistics
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def retrieve(self, request, *args, **kwargs):
        """
        Get customer statistics including invoice history
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Get recent invoices
        recent_invoices = instance.invoices.order_by('-created_at')[:5]
        
        from invoices.serializers import InvoiceListSerializer
        
        stats = {
            'customer': serializer.data,
            'recent_invoices': InvoiceListSerializer(
                recent_invoices,
                many=True
            ).data,
            'stats': {
                'total_invoices': instance.total_invoices,
                'total_amount': float(instance.total_amount),
                'average_invoice_amount': (
                    float(instance.total_amount / instance.total_invoices)
                    if instance.total_invoices > 0 else 0
                )
            }
        }
        
        return Response({
            'success': True,
            'data': stats
        }, status=status.HTTP_200_OK)