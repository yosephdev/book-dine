"""
URL configuration for BookDine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
import os
from django.http import HttpResponse

# Check if we're in emergency mode
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'BookDine.settings.emergency':
    # Use minimal emergency URLs
    from .urls_emergency import urlpatterns
else:
    # Regular imports for normal operation
    from django.conf import settings
    from django.conf.urls.static import static
    from django.contrib import admin
    from django.urls import path, include
    from booking_system import views as booking_views
    from .health import system_health

    # Custom error handlers
    handler404 = 'BookDine.views.custom_404_view'
    handler500 = 'BookDine.views.custom_500_view'

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('accounts/', include('allauth.urls')),
        path('accounts/', include('accounts.urls')),
        path('api/', include('booking_system.api_urls')),
        path('', lambda request: HttpResponse("BookDine is running!", content_type="text/html"), name='home'),
        path('health/', system_health, name='health'),
        path('book-table/', booking_views.book_table, name='book_table'),
        path('book-table/<uuid:restaurant_id>/', booking_views.book_table, name='book_table_restaurant'),
        path('reservations/', booking_views.my_reservations, name='my_reservations'),
        path('reservations/<uuid:reservation_id>/cancel/', booking_views.cancel_reservation, name='cancel_reservation'),
        path('restaurants/', booking_views.restaurant_list, name='restaurant_list'),
        path('restaurants/<uuid:restaurant_id>/', booking_views.restaurant_detail, name='restaurant_detail'),
        path('restaurants/<uuid:restaurant_id>/review/', booking_views.add_review, name='add_review'),
        path('search/', booking_views.search_restaurants, name='search_restaurants'),
        path('check-availability/', booking_views.check_availability_view, name='check_availability'),
    ]

    if settings.DEBUG:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        
        # Add debug toolbar URLs in development
        try:
            import debug_toolbar
            urlpatterns = [
                path('__debug__/', include(debug_toolbar.urls)),
            ] + urlpatterns
        except ImportError:
            pass
