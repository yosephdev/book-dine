from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'restaurants', api_views.RestaurantViewSet)
router.register(r'reservations', api_views.ReservationViewSet, basename='reservation')
router.register(r'reviews', api_views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    # path('docs/', include_docs_urls(title='BookDine API', description='Restaurant booking system API')),  # Temporarily disabled
    path('check-availability/', api_views.check_availability, name='check_availability'),
    path('dashboard/', api_views.dashboard_stats, name='dashboard_stats'),
    path('health/', api_views.api_health, name='api_health'),
]
