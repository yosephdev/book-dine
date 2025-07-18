from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import time, timedelta, datetime
import uuid

def get_midnight():
    """Return midnight time (00:00:00)"""
    return time(0, 0, 0)

class TimeStampedModel(models.Model):
    """Abstract base class with created_at and updated_at fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Restaurant(TimeStampedModel):
    CUISINE_CHOICES = [
        ('italian', 'Italian'),
        ('chinese', 'Chinese'),
        ('indian', 'Indian'),
        ('mexican', 'Mexican'),
        ('french', 'French'),
        ('japanese', 'Japanese'),
        ('american', 'American'),
        ('mediterranean', 'Mediterranean'),
        ('thai', 'Thai'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, db_index=True)
    location = models.CharField(max_length=200)
    cuisine = models.CharField(max_length=50, choices=CUISINE_CHOICES)
    description = models.TextField(blank=True, null=True)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='owned_restaurants'
    )
    
    # Operating hours
    opening_time = models.TimeField(default=time(9, 0))
    closing_time = models.TimeField(default=time(22, 0))
    
    class Meta:
        ordering = ['-rating', 'name']
        indexes = [
            models.Index(fields=['cuisine', 'rating']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        if self.opening_time >= self.closing_time:
            raise ValidationError('Opening time must be before closing time.')
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

class Table(TimeStampedModel):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    restaurant = models.ForeignKey(
        Restaurant, 
        on_delete=models.CASCADE, 
        related_name='tables'
    )
    table_number = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['restaurant', 'table_number']
        ordering = ['table_number']
    
    def __str__(self):
        return f"Table {self.table_number} at {self.restaurant.name}"
    
    def is_available(self, date, time, duration=timedelta(hours=2)):
        """Check if table is available for given date, time and duration"""
        if not self.is_active or self.status != 'available':
            return False
            
        start_datetime = timezone.datetime.combine(date, time)
        end_datetime = start_datetime + duration
        
        conflicting_reservations = self.reservations.filter(
            date=date,
            status__in=['confirmed', 'seated'],
            start_time__lt=end_datetime.time(),
            end_time__gt=start_datetime.time()
        )
        
        return not conflicting_reservations.exists()

class Reservation(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('seated', 'Seated'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    date = models.DateField(db_index=True)
    time = models.TimeField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    number_of_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Additional fields
    dietary_restrictions = models.TextField(blank=True, null=True)
    childs_chair = models.BooleanField(default=False)
    special_requests = models.TextField(blank=True, null=True)
    
    # Contact info
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    
    class Meta:
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['restaurant', 'date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.restaurant.name} on {self.date}"
    
    def clean(self):
        if self.date < timezone.now().date():
            raise ValidationError('Reservation date cannot be in the past.')
        
        if self.number_of_guests > self.table.capacity:
            raise ValidationError('Number of guests exceeds table capacity.')
    
    def save(self, *args, **kwargs):
        if not self.start_time:
            self.start_time = self.time
        if not self.end_time:
            # Default 2-hour reservation
            end_datetime = timezone.datetime.combine(
                timezone.now().date(), self.time
            ) + timedelta(hours=2)
            self.end_time = end_datetime.time()
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_past(self):
        return self.date < timezone.now().date()
    
    @property
    def can_be_cancelled(self):
        # Can cancel up to 2 hours before reservation
        reservation_datetime = timezone.datetime.combine(self.date, self.time)
        return (
            self.status in ['pending', 'confirmed'] and
            timezone.now() < reservation_datetime - timedelta(hours=2)
        )

class Review(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='review'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)  # For verified bookings
    
    class Meta:
        unique_together = ['user', 'restaurant']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.restaurant.name} ({self.rating}/5)"
