import os
from .base import *
from ..utils.env_validator import env_validator

# Security Settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# CSRF Protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = [
    'https://*.herokuapp.com',
    'https://yourdomain.com',
]

# Session Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "https:", "blob:")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)

# X-Frame-Options
X_FRAME_OPTIONS = 'DENY'

# Additional Security Headers
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
SECURE_CROSS_ORIGIN_EMBEDDER_POLICY = 'require-corp'

# Rate Limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'booking_system.validators.CustomPasswordValidator',
    },
]

# File Upload Security
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# Database Security
DATABASES['default']['OPTIONS'].update({
    'sslmode': 'require',
    'options': '-c default_transaction_isolation=serializable'
})

# Connection health checks for security
DATABASES['default']['CONN_HEALTH_CHECKS'] = True

# Logging Security
LOGGING['formatters']['security'] = {
    'format': '{levelname} {asctime} {name} {process:d} {thread:d} {message}',
    'style': '{',
}

LOGGING['handlers']['security'] = {
    'level': 'WARNING',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
    'maxBytes': 1024*1024*10,  # 10MB
    'backupCount': 5,
    'formatter': 'security',
}

LOGGING['loggers']['security'] = {
    'handlers': ['security'],
    'level': 'WARNING',
    'propagate': False,
}

# API Security
REST_FRAMEWORK.update({
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/min',
        'booking': '10/min',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
})

# Validate security-specific environment variables
REQUIRED_SECURITY_VARS = [
    'SECRET_KEY',
    'DATABASE_URL',
    'REDIS_URL',
    'EMAIL_HOST_PASSWORD',
    'CLOUDINARY_URL',
]

# Validate each required variable
for var in REQUIRED_SECURITY_VARS:
    if var.endswith('_URL'):
        env_validator.validate_url(var, required=True)
    else:
        env_validator.require_var(var)

# CSRF trusted origins validation
csrf_origins = env_validator.require_var('CSRF_TRUSTED_ORIGINS', default='https://*.herokuapp.com,https://yourdomain.com')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins.split(',')]

# Check for validation errors before proceeding
env_validator.check_errors()

# Security Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django_ratelimit.middleware.RatelimitMiddleware',
    'csp.middleware.CSPMiddleware',
] + MIDDLEWARE

# Additional Security Apps
INSTALLED_APPS += [
    'django_ratelimit',
    'csp',
    'axes',
]

# Django Axes (Brute Force Protection)
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1 hour
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_RESET_ON_SUCCESS = True
