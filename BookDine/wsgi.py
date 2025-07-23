"""
WSGI config for BookDine project.
"""
import os
from django.core.wsgi import get_wsgi_application

# Use emergency settings to avoid dependency issues
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BookDine.settings.emergency')

application = get_wsgi_application()
