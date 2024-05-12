from django.shortcuts import render
from .models import Restaurant, Reservation, Review

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


def book_table_view(request):
    context = {
    }
    return render(request, 'booking_system/book_table.html', context)


def view_reservations_view(request):
    # Get the user's reservations
    reservations = Reservation.objects.filter(user=request.user)
    context = {
        'reservations': reservations,
    }
    return render(request, 'booking_system/view_reservations.html', context)


def write_review_view(request):
    if request.method == 'POST':
        pass
    else:
        context = {
        }
        return render(request, 'booking_system/write_review.html', context)
