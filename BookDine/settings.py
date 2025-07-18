"""
Django settings for BookDine project.
Environment-specific settings loader.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Determine which settings to use based on environment
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    from .settings.production import *
elif ENVIRONMENT == 'security':
    from .settings.security import *
else:
    from .settings.development import *

# Override with any local settings if they exist
try:
    from .local_settings import *
except ImportError:
    pass
