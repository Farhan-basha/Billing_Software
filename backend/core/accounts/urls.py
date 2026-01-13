"""
URL routing for authentication endpoints
"""

from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView,
    UserProfileView, ChangePasswordView, UserListView
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # User management
    path('users/', UserListView.as_view(), name='user-list'),
]