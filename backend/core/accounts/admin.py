from django.contrib import admin

# Register your models here.
"""
Admin configuration for user management
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model
    """
    list_display = ['email', 'full_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'full_name', 'phone_number']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone_number')}),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_admin', 'is_superuser')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile model
    """
    list_display = ['user', 'city', 'state', 'created_at']
    search_fields = ['user__email', 'city', 'state']
    list_filter = ['state', 'created_at']