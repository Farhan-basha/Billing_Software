"""
Custom exception classes for the billing application
"""
from rest_framework import status
from rest_framework.exceptions import APIException


class BusinessException(APIException):
    """
    Base exception for business logic errors.
    Provides consistent error handling across the application.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(self, detail=None, code=None, status_code=None):
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code


class InvoiceException(BusinessException):
    """Exception for invoice-related errors"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred while processing the invoice.'
    default_code = 'invoice_error'


class CustomerException(BusinessException):
    """Exception for customer-related errors"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred while processing the customer.'
    default_code = 'customer_error'


class ValidationException(BusinessException):
    """Exception for validation errors"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation failed.'
    default_code = 'validation_error'


class ResourceNotFoundException(BusinessException):
    """Exception when a resource is not found"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'The requested resource was not found.'
    default_code = 'not_found'


class PermissionDeniedException(BusinessException):
    """Exception when user lacks permission"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'


class UnauthorizedException(BusinessException):
    """Exception when user is not authenticated"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication credentials were not provided.'
    default_code = 'unauthorized'
