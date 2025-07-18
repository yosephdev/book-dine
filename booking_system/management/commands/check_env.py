from django.core.management.base import BaseCommand
from django.conf import settings
from BookDine.utils.env_validator import EnvironmentValidator
import os

class Command(BaseCommand):
    help = 'Check environment variables configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--environment',
            type=str,
            default=os.environ.get('DJANGO_ENVIRONMENT', 'development'),
            help='Environment to check (development, production, security)'
        )

    def handle(self, *args, **options):
        environment = options['environment']
        self.stdout.write(f"Checking environment: {environment}")
        
        validator = EnvironmentValidator()
        
        # Common variables
        common_vars = ['SECRET_KEY', 'DEBUG']
        
        # Environment-specific variables
        env_vars = {
            'production': ['DATABASE_URL', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD', 'CLOUDINARY_URL'],
            'security': ['DATABASE_URL', 'REDIS_URL', 'EMAIL_HOST_PASSWORD', 'CLOUDINARY_URL'],
            'development': []
        }
        
        # Check common variables
        for var in common_vars:
            validator.require_var(var)
        
        # Check environment-specific variables
        for var in env_vars.get(environment, []):
            if var.endswith('_URL'):
                validator.validate_url(var)
            else:
                validator.require_var(var)
        
        try:
            validator.check_errors()
            self.stdout.write(
                self.style.SUCCESS(f'✅ All environment variables are properly configured for {environment}')
            )
        except ValueError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Environment configuration errors:\n{str(e)}')
            )
            return