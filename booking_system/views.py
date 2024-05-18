from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from googlemaps import Client
from googlemaps.exceptions import HTTPError, TransportError, ApiError
from .models import Restaurant, Reservation, Review, Table
from .forms import ReservationForm, ReviewForm

# Create your views here.


def home_view(request):
    featured_restaurants = Restaurant.objects.order_by('-rating')[:5]
    latest_reservations = Reservation.objects.order_by('-created_at')[:5]

    context = {
        'restaurants': featured_restaurants,
        'latest_reservations': latest_reservations,
    }
    return render(request, 'booking_system/home.html', context)


def book_table_view(request):
    search_query = request.GET.get('search', '')
    if search_query:
        client = Client(key=settings.GOOGLE_PLACES_API_KEY)
        places_results = client.places(
            query=search_query, location='New York City, NY', radius=5000)
        restaurants = places_results['results']
    else:
        restaurants = []

    context = {
        'restaurants': restaurants,
        'search_query': search_query,
    }
    return render(request, 'booking_system/book_table.html', context)


def restaurant_detail_view(request, place_id):
    client = Client(key=settings.GOOGLE_PLACES_API_KEY)
    place_details = client.place(place_id=place_id, fields=[
                                 'name', 'formatted_address', 'rating', 'user_ratings_total', 'opening_hours', 'website'])
    restaurant = place_details['result']
    print(restaurant)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = ReservationForm()

    context = {
        'restaurant': restaurant,
        'form': form,
        'place_id': place_id,
    }
    return render(request, 'booking_system/restaurant_detail.html', context)


def restaurant_list_view(request, place_id):
    search_query = request.GET.get('search', '')
    restaurants = Restaurant.objects.all()

    if search_query:
        restaurants = restaurants.filter(name__iexact=search_query)

    context = {
        'restaurants': restaurants,
        'search_query': search_query,
    }
    return render(request, 'booking_system/book_table.html', context)


@login_required
def make_reservation(request, place_id):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            table = form.cleaned_data['table']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']

            existing_reservations = Reservation.objects.filter(
                table=table,
                date=date,
                time=time,
            )

            if existing_reservations.exists():
                form.add_error(
                    None, 'The selected table is not available for the chosen date and time.')
            else:
                reservation = form.save(commit=False)
                reservation.user = request.user
                reservation.save()
                messages.success(
                    request, 'Your reservation has been made successfully.')
                return redirect('reservation_success')
    else:
        form = ReservationForm()
    context = {
        'form': form,
        'place_id': place_id,
    }
    return render(request, 'booking_system/make_reservation.html', context)


@login_required
def view_reservations_view(request):
    if request.user.is_authenticated:
      reservations = Reservation.objects.filter(user=request.user)
      context = {
          'reservations': reservations,
      }
      return render(request, 'booking_system/view_reservations.html', context)
    else:
        return redirect('account_login')


@login_required
def update_reservation_view(request, reservation_id):
    reservation = get_object_or_404(
        Reservation, id=reservation_id, user=request.user)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your reservation has been updated successfully.')
            return redirect('view_reservations')
    else:
        form = ReservationForm(instance=reservation)
    return render(request, 'booking_system/update_reservation.html', {'form': form})


@login_required
def cancel_reservation_view(request, reservation_id):
    reservation = get_object_or_404(
        Reservation, id=reservation_id, user=request.user)
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, 'Your reservation has been canceled.')
        return redirect('view_reservations')
    return render(request, 'booking_system/cancel_reservation.html', {'reservation': reservation})


@login_required
def write_review_view(request, place_id):
    try:
        client = Client(key=settings.GOOGLE_PLACES_API_KEY)
        place_details = client.place(place_id=place_id, fields=[
                                     'name', 'formatted_address', 'rating', 'user_ratings_total', 'opening_hours', 'website'])
        print(place_details)
        restaurant = place_details['result']
    except ApiError as e:
        if 'Invalid \'placeid\' parameter' in str(e):
            error_message = "The provided place ID is invalid. Please make sure you are using a valid Google Places API place ID."
            return render(request, 'booking_system/invalid_place_id.html', {'error_message': error_message})
        else:
            error_message = str(e)
            return render(request, 'booking_system/invalid_place_id.html', {'error_message': error_message})
    except (HTTPError, TransportError) as e:
        error_message = str(e)
        return render(request, 'booking_system/invalid_place_id.html', {'error_message': error_message})

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.place_id = place_id
            review.save()
            messages.success(
                request, 'Your review has been submitted successfully.')
            return redirect('restaurant_detail', place_id=place_id)
    else:
        form = ReviewForm()

    context = {
        'restaurant': restaurant,
        'form': form,
    }
    return render(request, 'booking_system/write_review.html', context)
