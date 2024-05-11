from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

# Register your models here.


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email',
                    'phone_number', 'date_of_birth', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'date_of_birth', 'profile_picture')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
