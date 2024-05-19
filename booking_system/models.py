from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta
from datetime import time


# Create your models here.


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    cuisine = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    opening_hours = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.name


class Table(models.Model):
    restaurant = models.ForeignKey(
        'Restaurant',
        on_delete=models.CASCADE,
        related_name='tables'
    )
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    table_number = models.PositiveIntegerField(unique=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ('available', 'Available'),
            ('reserved', 'Reserved'),
            ('occupied', 'Occupied'),
        ),
        default='available'
    )

    def __str__(self):
        return f"Table {self.table_number} ({self.capacity} seats)"

    def is_available(self, date, start_time, duration):
        start_datetime = timezone.datetime.combine(date, start_time)
        end_datetime = start_datetime + duration

        overlapping_reservations = Reservation.objects.filter(
            table=self,
            date=date,
            time__gte=start_datetime,
            time__lt=end_datetime
        )

        if overlapping_reservations.exists():
            return False
        return True


def get_midnight():
    return time(0, 0)


class Reservation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_reservations'
    )
    restaurant = models.ForeignKey(
        'Restaurant', on_delete=models.CASCADE, related_name='restaurant_reservations'
    )
    dietary_restrictions = models.TextField(blank=True, null=True)
    childs_chair = models.BooleanField(default=False)
    table = models.ForeignKey(
        'Table', on_delete=models.CASCADE, related_name='table_reservations'
    )
    date = models.DateField()
    time = models.TimeField()
    number_of_guests = models.IntegerField()
    special_requests = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reservation for {self.user.get_full_name()} on {self.date} at {self.time}"

    @property
    def start_time(self):
        return self.time - timedelta(seconds=7)

    @property
    def end_time(self):
        return self.time + timedelta(seconds=11)


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='reviews')
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.restaurant.name}"
