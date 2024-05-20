from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from accounts.admin import CustomUserAdmin
from accounts.models import CustomUser
from .models import Restaurant, Table, Reservation, Review

# Register your models here.


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'cuisine', 'rating')
    list_filter = ('cuisine', 'rating')

    def name(self, obj):
        return obj.name

    def location(self, obj):
        return obj.location

    def cuisine(self, obj):
        return obj.cuisine

    def rating(self, obj):
        return obj.rating


class AvailableFilter(admin.SimpleListFilter):
    title = _('Available')
    parameter_name = 'available'

    def lookups(self, request, model_admin):
        return (
            ('available', _('Available')),
            ('unavailable', _('Unavailable')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'available':
            return queryset.filter(status='available')
        elif value == 'unavailable':
            return queryset.exclude(status='available')
        return queryset


class TableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'capacity', 'restaurant', 'status')
    list_filter = ('restaurant', 'status')


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'table', 'restaurant', 'date',
                    'time', 'number_of_guests', 'created_at')
    list_filter = ('date', 'restaurant')
    search_fields = ('user__username', 'table__table_number')
    date_hierarchy = 'created_at'


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'rating', 'comment', 'created_at')
    list_filter = ('restaurant', 'rating')
    search_fields = ('user__username', 'restaurant__name', 'comment')
    date_hierarchy = 'created_at'


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Review, ReviewAdmin)
