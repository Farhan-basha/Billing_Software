"""
URL routing for invoice management endpoints
"""

from django.urls import path
from .views import (
    InvoiceListCreateView, InvoiceDetailView,
    InvoicePrintView, InvoiceStatusUpdateView,
    InvoiceDashboardView, InvoiceItemView
)

app_name = 'invoices'

urlpatterns = [
    # Invoice CRUD
    path('', InvoiceListCreateView.as_view(), name='invoice-list-create'),
    path('<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    
    # Invoice operations
    path('<int:pk>/print/', InvoicePrintView.as_view(), name='invoice-print'),
    path('<int:pk>/status/', InvoiceStatusUpdateView.as_view(), name='invoice-status'),
    
    # Dashboard
    path('dashboard/', InvoiceDashboardView.as_view(), name='invoice-dashboard'),
    
    # Invoice items
    path('items/<int:pk>/', InvoiceItemView.as_view(), name='invoice-item'),
]