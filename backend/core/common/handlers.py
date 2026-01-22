"""
Custom API exception handlers for consistent error responses
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error format across the API.
    
    Returns:
        Response with standardized error format including success flag and error details
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Log the error
        logger.error(
            f"API Error: {exc.__class__.__name__}",
            extra={
                'status_code': response.status_code,
                'error_detail': str(exc),
                'path': context.get('request').path,
            },
            exc_info=True
        )

        # Format the error response
        custom_response = {
            'success': False,
            'error': {
                'message': response.data.get('detail', str(exc)) if isinstance(response.data, dict) else str(exc),
                'code': exc.default_code if hasattr(exc, 'default_code') else 'error',
                'status_code': response.status_code,
                'details': response.data if isinstance(response.data, list) else response.data.get('detail', response.data),
            }
        }
        response.data = custom_response
    else:
        # Log unexpected errors
        logger.error(
            f"Unhandled Exception: {exc.__class__.__name__}",
            extra={'path': context.get('request').path if context.get('request') else 'unknown'},
            exc_info=True
        )

        # Return generic error response
        response = Response(
            {
                'success': False,
                'error': {
                    'message': 'An internal server error occurred.',
                    'code': 'internal_error',
                    'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
