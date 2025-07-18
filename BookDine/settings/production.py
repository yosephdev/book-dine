from .base import *
from ..utils.env_validator import env_validator
import dj_database_url

DEBUG = False

# Validate production-specific variables
ALLOWED_HOSTS = env_validator.require_var('ALLOWED_HOSTS', default='.herokuapp.com').split(',')
DATABASE_URL = env_validator.validate_url('DATABASE_URL', required=False)

# Email configuration validation
EMAIL_HOST_USER = env_validator.require_var('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env_validator.require_var('EMAIL_HOST_PASSWORD')

# Cloudinary validation
CLOUDINARY_URL = env_validator.validate_url('CLOUDINARY_URL', required=True)

# Production database configuration
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600, 
            ssl_require=True,
            conn_health_checks=True
        )
    }
else:
    # Fallback to base configuration with production SSL
    DATABASES['default']['OPTIONS'].update({
        'sslmode': 'require',
        'options': '-c default_transaction_isolation=serializable'
    })

# Email settings with validated credentials
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD

# Check for validation errors
env_validator.check_errors()
