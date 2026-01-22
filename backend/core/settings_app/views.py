from django.shortcuts import render

# Create your views here.
"""
Settings and configuration management views
"""
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from common.permissions import IsAdmin
from .models import CompanySettings
from .serializers import CompanySettingsSerializer
import logging

logger = logging.getLogger(__name__)


class CompanySettingsView(APIView):
    """
    API endpoint for company settings.
    - GET: Retrieve company settings (public)
    - PUT/PATCH: Update company settings (admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create the singleton company settings"""
        obj, created = CompanySettings.objects.get_or_create(pk=1)
        return obj
    
    def get(self, request):
        """
        Retrieve company settings
        
        Returns:
            Response with company settings data
        """
        try:
            settings = self.get_object()
            serializer = CompanySettingsSerializer(settings)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving company settings: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'Failed to retrieve company settings',
                    'code': 'settings_error'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """
        Update company settings (full update, requires all fields)
        
        Restricted to admin users only.
        """
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': {
                    'message': 'You do not have permission to update company settings',
                    'code': 'permission_denied'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            settings = self.get_object()
            serializer = CompanySettingsSerializer(settings, data=request.data, partial=False)
            
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Company settings updated by {request.user.email}")
                return Response({
                    'success': True,
                    'message': 'Company settings updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'error': {
                    'message': 'Validation failed',
                    'code': 'validation_error',
                    'details': serializer.errors
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating company settings: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'Failed to update company settings',
                    'code': 'settings_error'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request):
        """
        Partial update of company settings
        
        Restricted to admin users only.
        Only provided fields will be updated.
        """
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': {
                    'message': 'You do not have permission to update company settings',
                    'code': 'permission_denied'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            settings = self.get_object()
            serializer = CompanySettingsSerializer(settings, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Company settings partially updated by {request.user.email}")
                return Response({
                    'success': True,
                    'message': 'Company settings updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'error': {
                    'message': 'Validation failed',
                    'code': 'validation_error',
                    'details': serializer.errors
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating company settings: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'Failed to update company settings',
                    'code': 'settings_error'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompanySettingsPublicView(APIView):
    """
    Public API endpoint for company settings (no authentication required)
    Used by frontend for displaying company information
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Retrieve public company settings
        
        Returns only public-facing information
        """
        try:
            settings = CompanySettings.objects.first()
            
            if not settings:
                return Response({
                    'success': False,
                    'error': {
                        'message': 'Company settings not configured',
                        'code': 'settings_not_found'
                    }
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Return only public fields
            public_data = {
                'company_name': settings.company_name,
                'company_address': settings.company_address,
                'phone_number': settings.phone_number,
                'email': settings.email,
                'website': settings.website,
                'gstin': settings.gstin,
                'logo': settings.logo.url if settings.logo else None,
                'tax_label': settings.tax_label,
            }
            
            return Response({
                'success': True,
                'data': public_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving public company settings: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'Failed to retrieve company settings',
                    'code': 'settings_error'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

