from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Restaurant, Reservation
from .forms import ReservationForm, ReviewForm
import logging

# Create your views here.

import random

def home_view(request):
    featured_restaurants = Restaurant.objects.order_by('-rating')[:5]
    all_restaurants = Restaurant.objects.all()

    messages = [
        "Book your table now!",
        "Experience fine dining with us!",
        "Reserve your spot today!",
        "Taste the best in town!",
        "Your culinary journey begins here!",
    ]
    random_message = random.choice(messages)

    context = {
        'restaurants': featured_restaurants,
        'all_restaurants': all_restaurants,
        'random_message': random_message,
    }
    return render(request, 'booking_system/home.html', context)


def book_table_view(request):
    restaurants = Restaurant.objects.all()
    context = {
        'restaurants': restaurants,
    }
    return render(request, 'booking_system/book_table.html', context)


@login_required
def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    reviews = restaurant.reviews.all().order_by('-created_at')
    context = {
        'restaurant': restaurant,
        'reviews': reviews,
    }
    return render(request, 'booking_system/restaurant_detail.html', context)


from .forms import ReservationForm, ReviewForm, RestaurantFilterForm

def restaurant_list_view(request):
    restaurants = Restaurant.objects.all()
    form = RestaurantFilterForm(request.GET)

    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        cuisine = form.cleaned_data.get('cuisine')
        rating = form.cleaned_data.get('rating')

        if search_query:
            restaurants = restaurants.filter(name__icontains=search_query)
        if cuisine:
            restaurants = restaurants.filter(cuisine=cuisine)
        if rating:
            restaurants = restaurants.filter(rating__gte=rating)

    context = {
        'restaurants': restaurants,
        'form': form,
    }
    return render(request, 'booking_system/book_table.html', context)


logger = logging.getLogger(__name__)


@login_required
def create_reservation(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST, restaurant=restaurant)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.restaurant = restaurant
            reservation.save()
            messages.success(
                request, 'Your reservation has been made successfully.')
            return redirect('reservation_list')
    else:
        form = ReservationForm(restaurant=restaurant)

    return render(
        request,
        'booking_system/create_reservation.html',
        {'form': form, 'restaurant': restaurant}
        )


def reservation_list(request):
    reservations = Reservation.objects.all()
    return render(
        request, 'booking_system/reservation_list.html',
        {'reservations': reservations})


@login_required
def view_reservations(request):
    if request.user.is_authenticated:
        reservations = Reservation.objects.filter(user=request.user)
        context = {
            'reservations': reservations,
        }
        return render(
             request, 'booking_system/view_reservations.html', context)
    else:
        return redirect('account_login')


@login_required
def update_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation, pk=reservation_id, user=request.user)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your reservation has been updated successfully.')
            return redirect('view_reservations')
    else:
        form = ReservationForm(instance=reservation)
    return render(
        request, 'booking_system/update_reservation.html', {'form': form})


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation, id=reservation_id, user=request.user)
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, 'Your reservation has been canceled.')
        return redirect('view_reservations')
    return render(
        request, 'booking_system/cancel_reservation.html',
        {'reservation': reservation})


@login_required
def write_review_view(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.restaurant = restaurant
            review.save()
            messages.success(
                request, 'Your review has been submitted successfully.')
            return redirect('restaurant_detail', restaurant_id=restaurant_id)
    else:
        form = ReviewForm()
    return render(
        request, 'booking_system/write_review.html',
        {'form': form, 'restaurant': restaurant})


def search_restaurants(request):
    query = request.GET.get('q', '')
    restaurants = Restaurant.objects.filter(
        Q(name__icontains=query) |
        Q(cuisine__icontains=query) |
        Q(description__icontains=query)
    )
    context = {
        'restaurants': restaurants,
        'query': query,
    }
    return render(request, 'booking_system/search_results.html', context)
