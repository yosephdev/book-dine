from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Log the error for debugging
        view = context.get('view', None)
        request = context.get('request', None)
        
        logger.error(
            f"API Error in {view.__class__.__name__ if view else 'Unknown'}: "
            f"{exc.__class__.__name__}: {str(exc)}"
        )
        
        # Customize the error response format
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': response.data.get('detail', str(exc)),
            'errors': response.data if isinstance(response.data, dict) else None
        }
        
        response.data = custom_response_data
    
    return response