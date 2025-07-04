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
from django.urls import path, include
from booking_system import views as booking_views

# Custom error handlers
handler404 = 'BookDine.views.custom_404_view'
handler500 = 'BookDine.views.custom_500_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('', booking_views.home_view, name='home'),
    path('book-table/', booking_views.book_table_view, name='book_table'),
    path('reservations/', booking_views.view_reservations, name='view_reservations'),
    path('restaurants/<int:restaurant_id>/write-review/', booking_views.write_review_view, name='write_review'),
    path('reviews/<int:review_id>/update/', booking_views.update_review_view, name='update_review'),
    path('reviews/<int:review_id>/delete/', booking_views.delete_review_view, name='delete_review'),
    path('restaurants/<int:restaurant_id>/', booking_views.restaurant_detail, name='restaurant_detail'),
    path('restaurant/<int:restaurant_id>/create/', booking_views.create_reservation, name='create_reservation'),
    path('reservations/', booking_views.reservation_list, name='reservation_list'),
    path('reservations/<int:reservation_id>/update/', booking_views.update_reservation, name='update_reservation'),
    path('reservations/<int:reservation_id>/cancel/', booking_views.cancel_reservation, name='cancel_reservation'),
    path('restaurants/', booking_views.restaurant_list_view, name='restaurant_list'),
    path('search/', booking_views.search_restaurants, name='search_restaurants'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
