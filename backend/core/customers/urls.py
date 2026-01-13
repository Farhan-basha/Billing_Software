"""
URL routing for customer management endpoints
"""

from django.urls import path
from .views import (
    CustomerListCreateView, CustomerDetailView,
    CustomerSearchView, CustomerStatsView
)

app_name = 'customers'

urlpatterns = [
    # Customer CRUD
    path('', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
    
    # Customer search and stats
    path('search/', CustomerSearchView.as_view(), name='customer-search'),
    path('<int:pk>/stats/', CustomerStatsView.as_view(), name='customer-stats'),
]