from django.contrib import admin
from accounts.admin import CustomUserAdmin
from accounts.models import CustomUser
from .models import Restaurant, Table, Reservation, Review

# Register your models here.

admin.site.register(CustomUser, CustomUserAdmin)


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'cuisine', 'rating')
    search_fields = ('name', 'location', 'cuisine')
    list_filter = ('cuisine',)


class TableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'capacity', 'restaurant', 'status')
    list_filter = ('restaurant', 'status')
    search_fields = ('table_number', 'restaurant__name')


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'table', 'date', 'time', 'number_of_guests')
    list_filter = ('date', 'table__restaurant')
    search_fields = ('user__username', 'table__table_number')
    date_hierarchy = 'date'


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'rating', 'comment', 'created_at')
    list_filter = ('restaurant', 'rating')
    search_fields = ('user__username', 'restaurant__name', 'comment')
    date_hierarchy = 'created_at'


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Review, ReviewAdmin)
