from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg
from django.utils import timezone
from .models import Restaurant, Table, Reservation, Review

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'cuisine', 'location', 'rating', 'avg_rating_display',
        'review_count', 'is_active', 'created_at'
    ]
    list_filter = ['cuisine', 'is_active', 'created_at']
    search_fields = ['name', 'location', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'avg_rating_display']
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'location', 'cuisine', 'description', 'image')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Operating Hours', {
            'fields': ('opening_time', 'closing_time')
        }),
        ('Settings', {
            'fields': ('rating', 'is_active', 'user')
        }),
        ('Statistics', {
            'fields': ('avg_rating_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )
    
    def avg_rating_display(self, obj):
        if hasattr(obj, 'avg_rating') and obj.avg_rating:
            return f"{obj.avg_rating:.2f}"
        return "No reviews"
    avg_rating_display.short_description = "Average Rating"
    
    def review_count(self, obj):
        if hasattr(obj, 'review_count'):
            return obj.review_count
        return 0
    review_count.short_description = "Reviews"

class TableInline(admin.TabularInline):
    model = Table
    extra = 0
    fields = ['table_number', 'capacity', 'status', 'is_active']

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'restaurant', 'capacity', 'status', 'is_active']
    list_filter = ['status', 'is_active', 'restaurant__cuisine']
    search_fields = ['table_number', 'restaurant__name']
    list_editable = ['status', 'is_active']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'restaurant', 'table', 'date', 'time',
        'number_of_guests', 'status', 'created_at'
    ]
    list_filter = ['status', 'date', 'restaurant__cuisine', 'created_at']
    search_fields = ['user__username', 'restaurant__name', 'contact_email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Reservation Details', {
            'fields': ('id', 'user', 'restaurant', 'table', 'date', 'time', 'number_of_guests', 'status')
        }),
        ('Additional Information', {
            'fields': ('dietary_restrictions', 'childs_chair', 'special_requests'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('contact_phone', 'contact_email'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} reservations marked as confirmed.')
    mark_as_confirmed.short_description = "Mark selected reservations as confirmed"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} reservations marked as completed.')
    mark_as_completed.short_description = "Mark selected reservations as completed"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} reservations marked as cancelled.')
    mark_as_cancelled.short_description = "Mark selected reservations as cancelled"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'restaurant', 'rating', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified', 'created_at', 'restaurant__cuisine']
    search_fields = ['user__username', 'restaurant__name', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Review Details', {
            'fields': ('user', 'restaurant', 'reservation', 'rating', 'comment')
        }),
        ('Settings', {
            'fields': ('is_verified',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_verified', 'mark_as_unverified']
    
    def mark_as_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} reviews marked as verified.')
    mark_as_verified.short_description = "Mark selected reviews as verified"
    
    def mark_as_unverified(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} reviews marked as unverified.')
    mark_as_unverified.short_description = "Mark selected reviews as unverified"

# Customize admin site
admin.site.site_header = "BookDine Administration"
admin.site.site_title = "BookDine Admin"
admin.site.index_title = "Welcome to BookDine Administration"
