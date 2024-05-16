from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.db import models


# Create your models here.

class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_(
            "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(
        _('Phone Number'),
        max_length=15,
        validators=[phone_regex],
        blank=True,
        null=True,
        help_text=_('Enter your phone number in the format: "+999999999"')
    )
    date_of_birth = models.DateField(
        _('Date of Birth'),
        null=True,
        blank=True,
        help_text=_('Enter your date of birth in the format: YYYY-MM-DD')
    )
    profile_picture = models.ImageField(
        _('Profile Picture'),
        upload_to='profile_pictures',
        blank=True,
        null=True,
        help_text=_('Upload your profile picture')
    )

    def __str__(self):
        """
        Returns a string representation of the user.
        """
        return self.get_full_name() or self.username

    class Meta:
        """
        Meta class for CustomUser model.
        """
        db_table = 'accounts_customuser'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
