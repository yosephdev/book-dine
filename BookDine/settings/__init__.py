# Settings package
"""
Django settings package.
Import the appropriate settings based on DJANGO_SETTINGS_MODULE.
"""

# Fallback import to ensure basic settings are always available
import os
django_env = os.environ.get('DJANGO_SETTINGS_MODULE', '')

if 'production' in django_env:
    from .production import *
elif 'development' in django_env:
    from .development import *
else:
    # Fallback to base settings with essential configs
    from .base import *
    
    # Ensure critical settings are always set
    if not globals().get('ROOT_URLCONF'):
        ROOT_URLCONF = 'BookDine.urls'
    
    # Set debug based on environment
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
