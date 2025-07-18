"""
Django settings for BookDine project.
Environment-specific settings loader.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Determine which settings to use based on environment
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')

# Ensure we always have a fallback
try:
    if ENVIRONMENT == 'production':
        from .settings.production import *
    elif ENVIRONMENT == 'security':
        from .settings.security import *
    else:
        from .settings.development import *
except ImportError as e:
    # Fallback to base settings if specific environment fails
    print(f"Warning: Could not load {ENVIRONMENT} settings: {e}")
    from .settings.base import *

# Override with any local settings if they exist
try:
    from .local_settings import *
except ImportError:
    pass

# Ensure critical settings are always present
if not globals().get('ROOT_URLCONF'):
    ROOT_URLCONF = 'BookDine.urls'

if not globals().get('SECRET_KEY'):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-key-for-emergency')
