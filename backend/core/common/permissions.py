"""
Custom permission classes for fine-grained access control
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission that only allows admin users
    """
    message = 'Only administrators can access this resource.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission that allows only owners or admins to access
    """
    message = 'You do not have permission to access this resource.'

    def has_object_permission(self, request, view, obj):
        # Allow admin users
        if request.user and request.user.is_staff:
            return True
        # Allow owner
        return obj.created_by == request.user if hasattr(obj, 'created_by') else False


class IsOwner(permissions.BasePermission):
    """
    Permission that allows only the owner to access
    """
    message = 'You do not own this resource.'

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        return False
