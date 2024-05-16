from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.conf import settings
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


User = settings.AUTH_USER_MODEL


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ["username", "email",
                    "phone_number", "date_of_birth", "is_staff"]
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("phone_number", "date_of_birth", "profile_picture")}),
    )

    def get_queryset(self, request):
        """Limit non-superusers to only see their own profile."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)

    def has_change_permission(self, request, obj=None):
        """Allow users to view and edit their own profile, superusers can edit all."""
        if not obj:
            return True
        return obj.id == request.user.id or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Disallow the deletion of profiles via admin interface."""
        return False



