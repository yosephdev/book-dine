from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Restaurant, Reservation, Review, Table
from .forms import ReservationForm

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
    restaurants = Restaurant.objects.all()
    context = {
        'restaurants': restaurants,
    }
    return render(request, 'booking_system/book_table.html', context)


@login_required
def make_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            table = form.cleaned_data['table']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']

            # Check if the table is available for the given date and time
            existing_reservations = Reservation.objects.filter(
                Q(table=table) &
                Q(date=date) &
                Q(time=time)
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
    return render(request, 'booking_system/make_reservation.html', {'form': form})


def view_reservations_view(request):
    # Get the user's reservations
    reservations = Reservation.objects.filter(user=request.user)
    context = {
        'reservations': reservations,
    }
    return render(request, 'booking_system/view_reservations.html', context)


def update_reservation_view(request, reservation_id):
    reservation = get_object_or_404(
        Reservation, id=reservation_id, user=request.user)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
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
        return redirect('view_reservations')
    return render(request, 'booking_system/cancel_reservation.html', {'reservation': reservation})


def write_review_view(request):
    if request.method == 'POST':
        pass
    else:
        context = {
        }
        return render(request, 'booking_system/write_review.html', context)
