"""
Custom exception handler for consistent API error responses
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error format
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            'success': False,
            'error': {
                'message': str(exc),
                'details': response.data,
                'status_code': response.status_code
            }
        }
        response.data = custom_response
    
    return response


class BusinessException(Exception):
    """
    Base exception for business logic errors
    """
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvoiceException(BusinessException):
    """
    Exception for invoice-related errors
    """
    pass


class CustomerException(BusinessException):
    """
    Exception for customer-related errors
    """
    pass


class AuthenticationException(BusinessException):
    """
    Exception for authentication errors
    """
    def __init__(self, message):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)