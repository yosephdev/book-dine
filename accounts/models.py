from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.    
    """
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures', blank=True, null=True)

    def __str__(self):
        """
        Returns a string representation of the user.
        """
        return self.username

    class Meta:
        """
        Meta class for CustomUser model.
        """
        db_table = 'accounts_customuser'
        verbose_name = 'User'
        verbose_name_plural = 'Users'