from django.core.cache import cache
from django.db.models import Avg, Count
from .models import Restaurant, Reservation, Review
import hashlib

def get_cache_key(prefix, *args):
    """Generate a cache key from prefix and arguments"""
    key_data = f"{prefix}:{'_'.join(str(arg) for arg in args)}"
    return hashlib.md5(key_data.encode()).hexdigest()

def get_restaurant_stats(restaurant_id, cache_timeout=300):
    """Get cached restaurant statistics"""
    cache_key = get_cache_key('restaurant_stats', restaurant_id)
    stats = cache.get(cache_key)
    
    if stats is None:
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            stats = {
                'total_reservations': restaurant.reservations.count(),
                'avg_rating': restaurant.reviews.aggregate(
                    avg=Avg('rating')
                )['avg'] or 0,
                'review_count': restaurant.reviews.count(),
                'completed_reservations': restaurant.reservations.filter(
                    status='completed'
                ).count(),
            }
            cache.set(cache_key, stats, cache_timeout)
        except Restaurant.DoesNotExist:
            stats = {}
    
    return stats

def get_popular_restaurants(limit=10, cache_timeout=600):
    """Get cached list of popular restaurants"""
    cache_key = get_cache_key('popular_restaurants', limit)
    restaurants = cache.get(cache_key)
    
    if restaurants is None:
        restaurants = list(
            Restaurant.objects.active()
            .with_ratings()
            .order_by('-avg_rating', '-review_count')[:limit]
            .values('id', 'name', 'cuisine', 'location', 'avg_rating', 'review_count')
        )
        cache.set(cache_key, restaurants, cache_timeout)
    
    return restaurants

def get_cuisine_stats(cache_timeout=1800):
    """Get cached cuisine statistics"""
    cache_key = 'cuisine_stats'
    stats = cache.get(cache_key)
    
    if stats is None:
        stats = list(
            Restaurant.objects.active()
            .values('cuisine')
            .annotate(
                count=Count('id'),
                avg_rating=Avg('reviews__rating')
            )
            .order_by('-count')
        )
        cache.set(cache_key, stats, cache_timeout)
    
    return stats

def invalidate_restaurant_cache(restaurant_id):
    """Invalidate all cache entries related to a restaurant"""
    cache_keys = [
        get_cache_key('restaurant_stats', restaurant_id),
        'popular_restaurants_10',
        'cuisine_stats',
        'home_stats',
    ]
    
    cache.delete_many(cache_keys)

def get_user_reservation_stats(user_id, cache_timeout=300):
    """Get cached user reservation statistics"""
    cache_key = get_cache_key('user_reservation_stats', user_id)
    stats = cache.get(cache_key)
    
    if stats is None:
        reservations = Reservation.objects.filter(user_id=user_id)
        stats = {
            'total_reservations': reservations.count(),
            'upcoming_reservations': reservations.upcoming().count(),
            'completed_reservations': reservations.filter(status='completed').count(),
            'cancelled_reservations': reservations.filter(status='cancelled').count(),
        }
        cache.set(cache_key, stats, cache_timeout)
    
    return stats