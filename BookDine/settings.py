"""
Django settings for BookDine project.
This file is kept for backward compatibility.
The actual settings are now in the settings/ package.
"""

# Import from the settings package
try:
    from .settings.production import *
except ImportError:
    # Fallback for development
    try:
        from .settings.development import *
    except ImportError:
        from .settings.base import *
