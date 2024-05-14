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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', booking_views.home_view, name='home'),
    path('book-table/', booking_views.book_table_view, name='book_table'),
    path('view-reservations/', booking_views.view_reservations_view,
         name='view_reservations'),
    path('write-review/', booking_views.write_review_view, name='write_review'),
    path('make-reservation/', booking_views.make_reservation,
         name='make_reservation'),
    path('reservation/<int:reservation_id>/update/',
         booking_views.update_reservation_view, name='update_reservation'),
    path('reservation/<int:reservation_id>/cancel/',
         booking_views.cancel_reservation_view, name='cancel_reservation'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
