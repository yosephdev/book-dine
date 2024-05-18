from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.db import models


# Create your models here.

class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    ADMIN = 'admin'
    RESTAURANT_OWNER = 'restaurant_owner'
    CUSTOMER = 'customer'

    ROLES = (
        (ADMIN, 'Admin'),
        (RESTAURANT_OWNER, 'Restaurant Owner'),
        (CUSTOMER, 'Customer'),
    )

    role = models.CharField(max_length=20, choices=ROLES, default=CUSTOMER)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

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
