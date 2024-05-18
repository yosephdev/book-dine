from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name',
         'last_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

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
