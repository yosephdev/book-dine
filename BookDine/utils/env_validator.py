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
        
        if value and not (value.startswith('http://') or value.startswith('https://') or value.startswith('redis://')):
            self.invalid_vars.append(f"{var_name} (invalid URL format)")
            return None
        
        return value
    
    def check_errors(self):
        """Check for validation errors and raise if any found"""
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