from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import time, timedelta


# Create your models here.
def get_midnight():
    return time(0, 0)


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    cuisine = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='owned_restaurants'
    )

    def __str__(self):
        return self.name


class Table(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='tables')
    table_number = models.CharField(max_length=10)
    capacity = models.IntegerField()
    status = models.CharField(max_length=20, choices=[(
        'available', 'Available'), ('occupied', 'Occupied')])

    def is_available(self, date, time, duration):
        start_time = timezone.datetime.combine(date, time)
        end_time = start_time + duration
        reservations = self.reservations.filter(
            date=date,
            start_time__lt=end_time.time(),
            end_time__gt=start_time.time()
        )
        return not reservations.exists()

    def __str__(self):
        return f"Table {self.table_number} at {self.restaurant.name}"


class Reservation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reservations'
    )
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='reservations'
    )
    dietary_restrictions = models.TextField(blank=True, null=True)
    childs_chair = models.BooleanField(default=False)
    table = models.ForeignKey(
        Table, on_delete=models.CASCADE, related_name='reservations'
    )
    date = models.DateField()
    time = models.TimeField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    number_of_guests = models.IntegerField()
    special_requests = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.start_time:
            self.start_time = self.calculate_start_time()
        if not self.end_time:
            self.end_time = self.calculate_end_time()
        super().save(*args, **kwargs)

    def calculate_start_time(self):
        reservation_datetime = timezone.datetime.combine(self.date, self.time)
        start_time = reservation_datetime - timedelta(seconds=7)
        return start_time.time()

    def calculate_end_time(self):
        reservation_datetime = timezone.datetime.combine(self.date, self.time)
        end_time = reservation_datetime + timedelta(seconds=11)
        return end_time.time()

    def __str__(self):
        user_name = self.user.get_full_name()
        return f"Reservation for {user_name} on {self.date} at {self.time}"


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="reviews"
    )
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.restaurant.name}"
