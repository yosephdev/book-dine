#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == '__main__':
    # Set default settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BookDine.settings.development')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Custom commands for development
    if len(sys.argv) > 1:
        if sys.argv[1] == 'setup_dev':
            # Development setup command
            commands = [
                ['migrate'],
                ['collectstatic', '--noinput'],
                ['loaddata', 'fixtures/sample_data.json'],
                ['createsuperuser', '--noinput'] if not os.environ.get('DJANGO_SUPERUSER_USERNAME') else None
            ]
            
            for cmd in commands:
                if cmd:
                    print(f"Running: python manage.py {' '.join(cmd)}")
                    execute_from_command_line(['manage.py'] + cmd)
            
            print("Development setup complete!")
            sys.exit()
    
    execute_from_command_line(sys.argv)
