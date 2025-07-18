from django.db import models
from django.utils import timezone
from django.core.cache import cache

class RestaurantManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('user')
    
    def active(self):
        return self.filter(is_active=True)
    
    def with_ratings(self):
        return self.annotate(
            avg_rating=models.Avg('reviews__rating'),
            review_count=models.Count('reviews')
        )
    
    def by_cuisine(self, cuisine):
        return self.filter(cuisine=cuisine)
    
    def search(self, query):
        return self.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(location__icontains=query)
        )

class ReservationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('user', 'restaurant', 'table')
    
    def upcoming(self):
        return self.filter(date__gte=timezone.now().date())
    
    def past(self):
        return self.filter(date__lt=timezone.now().date())
    
    def by_status(self, status):
        return self.filter(status=status)
    
    def for_user(self, user):
        return self.filter(user=user)
    
    def for_restaurant(self, restaurant):
        return self.filter(restaurant=restaurant)
    
    def today(self):
        return self.filter(date=timezone.now().date())
    
    def this_week(self):
        today = timezone.now().date()
        week_start = today - timezone.timedelta(days=today.weekday())
        week_end = week_start + timezone.timedelta(days=6)
        return self.filter(date__range=[week_start, week_end])

class TableManager(models.Manager):
    def available(self):
        return self.filter(is_active=True, status='available')
    
    def for_restaurant(self, restaurant):
        return self.filter(restaurant=restaurant)
    
    def with_capacity(self, min_capacity):
        return self.filter(capacity__gte=min_capacity)

class ReviewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('user', 'restaurant')
    
    def verified(self):
        return self.filter(is_verified=True)
    
    def for_restaurant(self, restaurant):
        return self.filter(restaurant=restaurant)
    
    def by_rating(self, rating):
        return self.filter(rating=rating)
    
    def recent(self, days=30):
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)