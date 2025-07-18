import django_filters
from .models import Restaurant, Reservation, Review

class RestaurantFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    cuisine = django_filters.CharFilter(lookup_expr='icontains')
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    
    class Meta:
        model = Restaurant
        fields = ['name', 'location', 'cuisine', 'rating_min', 'rating_max']

class ReservationFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    
    class Meta:
        model = Reservation
        fields = ['status', 'restaurant', 'date_from', 'date_to']

class ReviewFilter(django_filters.FilterSet):
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    
    class Meta:
        model = Review
        fields = ['restaurant', 'rating', 'rating_min', 'rating_max', 'is_verified']
