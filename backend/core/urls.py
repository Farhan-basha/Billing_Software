"""
URL Configuration for Standard Steels & Hardware
Main routing file connecting all app endpoints
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    path('', include('core.urls')), 
    
    # API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/invoices/', include('invoices.urls')),
    path('api/settings/', include('settings_app.urls')),
    
    # JWT Token refresh
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = 'Standard Steels & Hardware Administration'
admin.site.site_title = 'SS&H Admin Portal'
admin.site.index_title = 'Welcome to SS&H Billing System'