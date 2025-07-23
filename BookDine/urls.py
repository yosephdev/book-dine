"""
URL configuration for BookDine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from booking_system import views as booking_views
from .health import system_health

# Custom error handlers
handler404 = 'BookDine.views.custom_404_view'
handler500 = 'BookDine.views.custom_500_view'

def home(request):
    return HttpResponse("""
    <h1>BookDine Emergency Mode</h1>
    <p>App is running in emergency mode</p>
    <ul>
        <li><a href="/health/">Health Check</a></li>
        <li><a href="/admin/">Admin (if available)</a></li>
    </ul>
    """, content_type="text/html")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('api/', include('booking_system.api_urls')),
    path('', home, name='home'),
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
