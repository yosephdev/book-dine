"""
Heroku-specific settings for Django.
Inherits from the base settings and overrides specific settings for production.
"""
from .base import *
import dj_database_url
import os

# Production specific settings inherited from base.py, with overrides below.

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Override ALLOWED_HOSTS for Heroku
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.herokuapp.com,localhost').split(',')

# Database configuration from Heroku's DATABASE_URL
# This overrides the DATABASES setting in base.py
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )
}

# Override static files storage for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Override logging for Heroku to output to console
# This will replace the LOGGING configuration from base.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# All other settings (INSTALLED_APPS, MIDDLEWARE, etc.) are inherited from base.py
