from django.shortcuts import render

# Create your views here.
"""
Invoice management views with comprehensive CRUD and reporting
"""

from rest_framework import status, generics, filters, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Invoice, InvoiceItem
from .serializers import (
    InvoiceSerializer, InvoiceListSerializer,
    InvoiceCreateSerializer, InvoiceUpdateSerializer,
    InvoicePrintSerializer, InvoiceItemSerializer
)


class InvoiceListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list and create invoices
    """
    queryset = Invoice.objects.all().select_related('customer', 'created_by')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'customer', 'invoice_date']
    search_fields = ['invoice_number', 'customer_name', 'customer_phone']
    ordering_fields = ['invoice_date', 'created_at', 'grand_total']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        Use different serializers for list and create
        """
        if self.request.method == 'POST':
            return InvoiceCreateSerializer
        return InvoiceListSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(invoice_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(invoice_date__lte=end_date)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Return paginated list of invoices
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
        
        # Calculate summary
        summary = queryset.aggregate(
            total_amount=Sum('grand_total'),
            total_invoices=Count('id')
        )
        
        return Response({
            'success': True,
            'count': queryset.count(),
            'summary': {
                'total_amount': float(summary['total_amount'] or 0),
                'total_invoices': summary['total_invoices']
            },
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        """
        Create new invoice with items
        """
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Invoice created successfully',
            'data': InvoiceSerializer(invoice).data
        }, status=status.HTTP_201_CREATED)


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, and delete invoice
    """
    queryset = Invoice.objects.all().select_related('customer', 'created_by').prefetch_related('items')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Use different serializers based on method
        """
        if self.request.method in ['PUT', 'PATCH']:
            return InvoiceUpdateSerializer
        return InvoiceSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """
        Get invoice details with items
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """
        Update invoice information
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Prevent updating paid or cancelled invoices
        if instance.status in ['paid', 'cancelled']:
            return Response({
                'success': False,
                'message': f'Cannot update {instance.status} invoice'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Invoice updated successfully',
            'data': InvoiceSerializer(invoice).data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete invoice (only draft invoices)
        """
        instance = self.get_object()
        
        # Only allow deleting draft invoices
        if instance.status != 'draft':
            return Response({
                'success': False,
                'message': 'Only draft invoices can be deleted'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        customer = instance.customer
        instance.delete()
        
        # Update customer totals
        customer.update_totals()
        
        return Response({
            'success': True,
            'message': 'Invoice deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class InvoicePrintView(generics.RetrieveAPIView):
    """
    API endpoint to get invoice in print format
    """
    queryset = Invoice.objects.all().select_related('customer').prefetch_related('items')
    serializer_class = InvoicePrintSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def retrieve(self, request, *args, **kwargs):
        """
        Get invoice data formatted for printing
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Get company settings
        from settings_app.models import CompanySettings
        company = CompanySettings.get_settings()
        
        response_data = {
            'success': True,
            'data': {
                'invoice': serializer.data,
                'company': {
                    'name': company.company_name,
                    'address': company.company_address,
                    'phone': company.phone_number,
                    'email': company.email,
                    'gstin': company.gstin,
                }
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class InvoiceStatusUpdateView(APIView):
    """
    API endpoint to update invoice status
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """
        Update invoice status (mark as sent, paid, or cancelled)
        """
        try:
            invoice = Invoice.objects.get(pk=pk)
        except Invoice.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invoice not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        
        if new_status not in ['sent', 'paid', 'cancelled']:
            return Response({
                'success': False,
                'message': 'Invalid status. Must be: sent, paid, or cancelled'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update status
        invoice.status = new_status
        invoice.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'Invoice marked as {new_status}',
            'data': InvoiceSerializer(invoice).data
        }, status=status.HTTP_200_OK)


class InvoiceDashboardView(APIView):
    """
    API endpoint for dashboard statistics
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get dashboard statistics and recent invoices
        """
        # Date filters
        today = timezone.now().date()
        this_month_start = today.replace(day=1)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        
        # Overall statistics
        total_stats = Invoice.objects.aggregate(
            total_invoices=Count('id'),
            total_amount=Sum('grand_total')
        )
        
        # This month statistics
        this_month_stats = Invoice.objects.filter(
            invoice_date__gte=this_month_start
        ).aggregate(
            total_invoices=Count('id'),
            total_amount=Sum('grand_total')
        )
        
        # Last month statistics
        last_month_stats = Invoice.objects.filter(
            invoice_date__gte=last_month_start,
            invoice_date__lt=this_month_start
        ).aggregate(
            total_invoices=Count('id'),
            total_amount=Sum('grand_total')
        )
        
        # Status breakdown
        status_stats = {
            'draft': Invoice.objects.filter(status='draft').count(),
            'sent': Invoice.objects.filter(status='sent').count(),
            'paid': Invoice.objects.filter(status='paid').count(),
            'cancelled': Invoice.objects.filter(status='cancelled').count(),
        }
        
        # Recent invoices
        recent_invoices = Invoice.objects.order_by('-created_at')[:10]
        
        # Top customers
        from customers.models import Customer
        top_customers = Customer.objects.filter(
            is_active=True
        ).order_by('-total_amount')[:5]
        
        from customers.serializers import CustomerListSerializer
        
        dashboard_data = {
            'overall': {
                'total_invoices': total_stats['total_invoices'],
                'total_amount': float(total_stats['total_amount'] or 0)
            },
            'this_month': {
                'total_invoices': this_month_stats['total_invoices'],
                'total_amount': float(this_month_stats['total_amount'] or 0)
            },
            'last_month': {
                'total_invoices': last_month_stats['total_invoices'],
                'total_amount': float(last_month_stats['total_amount'] or 0)
            },
            'status_breakdown': status_stats,
            'recent_invoices': InvoiceListSerializer(
                recent_invoices,
                many=True
            ).data,
            'top_customers': CustomerListSerializer(
                top_customers,
                many=True
            ).data
        }
        
        return Response({
            'success': True,
            'data': dashboard_data
        }, status=status.HTTP_200_OK)


class InvoiceItemView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to manage individual invoice items
    """
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_destroy(self, instance):
        """
        Delete item and recalculate invoice
        """
        invoice = instance.invoice
        instance.delete()
        invoice.calculate_totals()