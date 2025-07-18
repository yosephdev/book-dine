import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    """
    Custom password validator with additional security requirements
    """
    def validate(self, password, user=None):
        if len(password) < 12:
            raise ValidationError(
                _("Password must be at least 12 characters long."),
                code='password_too_short',
            )
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
        
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter."),
                code='password_no_lower',
            )
        
        if not re.search(r'\d', password):
            raise ValidationError(
                _("Password must contain at least one digit."),
                code='password_no_digit',
            )
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("Password must contain at least one special character."),
                code='password_no_special',
            )
        
        # Check for common patterns
        common_patterns = [
            r'123',
            r'abc',
            r'qwerty',
            r'password',
            r'admin',
        ]
        
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                raise ValidationError(
                    _("Password contains common patterns that are not allowed."),
                    code='password_common_pattern',
                )

    def get_help_text(self):
        return _(
            "Your password must contain at least 12 characters, including "
            "uppercase and lowercase letters, digits, and special characters."
        )

def validate_phone_number(value):
    """Validate phone number format"""
    phone_regex = re.compile(r'^\+?1?\d{9,15}$')
    if not phone_regex.match(value):
        raise ValidationError(
            _('Enter a valid phone number.'),
            code='invalid_phone',
        )

def validate_image_file(value):
    """Validate uploaded image files"""
    import os
    from django.conf import settings
    
    # Check file extension
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            _('Unsupported file extension. Allowed extensions: %(extensions)s'),
            code='invalid_extension',
            params={'extensions': ', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)},
        )
    
    # Check file size
    if value.size > settings.MAX_IMAGE_SIZE:
        raise ValidationError(
            _('File too large. Size should not exceed %(max_size)s MB.'),
            code='file_too_large',
            params={'max_size': settings.MAX_IMAGE_SIZE // (1024 * 1024)},
        )

def validate_reservation_time(value):
    """Validate reservation time is within business hours"""
    from datetime import time
    
    # Business hours: 9 AM to 11 PM
    if not (time(9, 0) <= value <= time(23, 0)):
        raise ValidationError(
            _('Reservation time must be between 9:00 AM and 11:00 PM.'),
            code='invalid_time',
        )