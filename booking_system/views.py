from django.shortcuts import render
from .models import Restaurant, Reservation

# Create your views here.

def home_view(request):
    # Get the featured restaurants
    featured_restaurants = Restaurant.objects.order_by('-rating')[:5]

    # Get the latest reservations
    latest_reservations = Reservation.objects.order_by('-created_at')[:5]

    context = {
        'restaurants': featured_restaurants,
        'latest_reservations': latest_reservations,
    }
    return render(request, 'booking_system/home.html', context)