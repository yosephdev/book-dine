import os
import sys
from typing import List, Dict, Any

class EnvironmentValidator:
    """Utility class for validating required environment variables"""
    
    def __init__(self):
        self.missing_vars = []
        self.invalid_vars = []
    
    def require_var(self, var_name: str, var_type: type = str, default: Any = None):
        """Validate that a required environment variable exists and is valid"""
        value = os.environ.get(var_name, default)
        
        if value is None:
            self.missing_vars.append(var_name)
            return None
        
        # Type conversion and validation
        try:
            if var_type == bool:
                return value.lower() in ('true', '1', 'yes', 'on')
            elif var_type == int:
                return int(value)
            elif var_type == float:
                return float(value)
            else:
                return str(value)
        except (ValueError, TypeError):
            self.invalid_vars.append(f"{var_name} (expected {var_type.__name__})")
            return None
    
    def validate_url(self, var_name: str, required: bool = True):
        """Validate URL format"""
        value = os.environ.get(var_name)
        if not value and required:
            self.missing_vars.append(var_name)
            return None
        
        if not value:
            return None
        
        # Accept common URL schemes for different services
        valid_schemes = [
            'http://', 'https://',  # Web URLs
            'postgres://', 'postgresql://',  # PostgreSQL
            'mysql://', 'sqlite://',  # Other databases  
            'redis://', 'rediss://',  # Redis
            'cloudinary://',  # Cloudinary
            'mongodb://',  # MongoDB
            'ftp://', 'ftps://',  # FTP
        ]
        
        if not any(value.startswith(scheme) for scheme in valid_schemes):
            self.invalid_vars.append(f"{var_name} (invalid URL format)")
            return None
        
        return value
    
    def check_errors(self):
        """Check for validation errors and raise if any found"""
        # In production environments (like Heroku), be more lenient
        is_production = os.environ.get('DJANGO_ENV') == 'production' or \
                       os.environ.get('DYNO') is not None or \
                       os.environ.get('PORT') is not None
        
        if is_production:
            # In production, only log warnings instead of raising errors
            if self.missing_vars or self.invalid_vars:
                warnings = []
                if self.missing_vars:
                    warnings.append(f"Warning - Missing environment variables: {', '.join(self.missing_vars)}")
                if self.invalid_vars:
                    warnings.append(f"Warning - Invalid environment variables: {', '.join(self.invalid_vars)}")
                
                warning_message = "\n".join(warnings)
                print(f"Environment Configuration Warnings:\n{warning_message}", file=sys.stderr)
                
                # Clear the errors so they don't accumulate
                self.missing_vars.clear()
                self.invalid_vars.clear()
            return
        
        # For development, still raise errors
        errors = []
        
        if self.missing_vars:
            errors.append(f"Missing required environment variables: {', '.join(self.missing_vars)}")
        
        if self.invalid_vars:
            errors.append(f"Invalid environment variables: {', '.join(self.invalid_vars)}")
        
        if errors:
            error_message = "\n".join(errors)
            print(f"Environment Configuration Error:\n{error_message}", file=sys.stderr)
            raise ValueError(error_message)

# Global validator instance
env_validator = EnvironmentValidator()