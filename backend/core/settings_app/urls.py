"""
URL routing for company settings endpoints
"""

from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import CompanySettings

class CompanySettingsView(APIView):
    """
    API endpoint to get and update company settings
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get company settings
        """
        settings = CompanySettings.get_settings()
        
        data = {
            'company_name': settings.company_name,
            'company_address': settings.company_address,
            'phone_number': settings.phone_number,
            'email': settings.email,
            'website': settings.website,
            'gstin': settings.gstin,
            'default_tax_rate': float(settings.default_tax_rate),
            'tax_label': settings.tax_label,
            'invoice_prefix': settings.invoice_prefix,
            'invoice_start_number': settings.invoice_start_number,
            'invoice_terms': settings.invoice_terms,
            'invoice_footer': settings.invoice_footer,
            'payment_due_days': settings.payment_due_days,
            'bank_name': settings.bank_name,
            'account_number': settings.account_number,
            'ifsc_code': settings.ifsc_code,
        }
        
        return Response({
            'success': True,
            'data': data
        }, status=status.HTTP_200_OK)
    
    def put(self, request):
        """
        Update company settings (admin only)
        """
        if not request.user.is_administrator:
            return Response({
                'success': False,
                'message': 'Only administrators can update settings'
            }, status=status.HTTP_403_FORBIDDEN)
        
        settings = CompanySettings.get_settings()
        
        # Update fields
        for field, value in request.data.items():
            if hasattr(settings, field):
                setattr(settings, field, value)
        
        settings.save()
        
        return Response({
            'success': True,
            'message': 'Settings updated successfully'
        }, status=status.HTTP_200_OK)

app_name = 'settings_app'

urlpatterns = [
    path('company/', CompanySettingsView.as_view(), name='company-settings'),
]