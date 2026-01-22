"""
URL routing for company settings endpoints
"""

from django.urls import path
from .views import (
    CompanySettingsView,
    CompanySettingsPublicView,
)

app_name = 'settings_app'

urlpatterns = [
    # Private settings endpoint (admin only)
    path('company/', CompanySettingsView.as_view(), name='company-settings'),
    
    # Public settings endpoint (no auth required)
    path('company/public/', CompanySettingsPublicView.as_view(), name='company-settings-public'),
]
