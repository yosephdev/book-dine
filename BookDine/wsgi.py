"""
WSGI config for BookDine project.
"""
import os
from django.core.wsgi import get_wsgi_application

# Use production settings for Heroku
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BookDine.settings.heroku')

application = get_wsgi_application()
