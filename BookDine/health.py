"""
Emergency health check module
"""
import os
import sys
from django.http import JsonResponse
from django.conf import settings

def system_health(request):
    """System health check endpoint"""
    health_data = {
        'status': 'ok',
        'django_version': getattr(settings, 'DJANGO_VERSION', 'unknown'),
        'debug': getattr(settings, 'DEBUG', False),
        'database': 'configured',
        'static_files': 'configured',
        'environment': os.environ.get('DJANGO_SETTINGS_MODULE', 'unknown'),
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }
    
    # Test database connection
    try:
        from django.db import connection
        connection.ensure_connection()
        health_data['database'] = 'connected'
    except Exception as e:
        health_data['database'] = f'error: {str(e)}'
        health_data['status'] = 'degraded'
    
    return JsonResponse(health_data)