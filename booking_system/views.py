from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Restaurant, Reservation, Review, Table
from .forms import ReservationForm, ReviewForm

@cache_page(60 * 15)  # Cache for 15 minutes
def home(request):
    """Enhanced home view with featured restaurants and statistics"""
    return render(request, 'booking_system/home.html')

def restaurant_list(request):
    """Restaurant list view with filtering and search"""
    return render(request, 'booking_system/restaurant_list.html')

def restaurant_detail(request, restaurant_id):
    """Restaurant detail view with reviews and booking form"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, is_active=True)
    
    # Get reviews with pagination
    reviews = restaurant.reviews.all().order_by('-created_at')
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_reviews = paginator.get_page(page_number)
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'restaurant': restaurant,
        'reviews': page_reviews,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': reviews.count(),
    }
    
    return render(request, 'booking_system/restaurant_detail.html', context)

@login_required
def book_table(request, restaurant_id=None):
    """Book table view - can be for specific restaurant or general booking"""
    restaurant = None
    if restaurant_id:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, is_active=True)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            
            # Find available table
            available_tables = Table.objects.filter(
                restaurant=reservation.restaurant,
                capacity__gte=reservation.number_of_guests,
                is_active=True
            ).exclude(
                reservations__date=reservation.date,
                reservations__time=reservation.time,
                reservations__status__in=['confirmed', 'pending']
            )
            
            if available_tables.exists():
                reservation.table = available_tables.first()
                reservation.save()
                messages.success(request, 'Your reservation has been confirmed!')
                return redirect('my_reservations')
            else:
                messages.error(request, 'No tables available for the selected time.')
    else:
        initial_data = {}
        if restaurant:
            initial_data['restaurant'] = restaurant
        form = ReservationForm(initial=initial_data)
    
    context = {
        'form': form,
        'restaurant': restaurant,
        'restaurants': Restaurant.objects.filter(is_active=True) if not restaurant else None,
    }
    
    return render(request, 'booking_system/book_table.html', context)

@login_required
def my_reservations(request):
    """User's reservations view"""
    upcoming_reservations = Reservation.objects.filter(
        user=request.user,
        date__gte=timezone.now().date(),
        status__in=['confirmed', 'pending']
    ).order_by('date', 'time')
    
    past_reservations = Reservation.objects.filter(
        user=request.user,
        date__lt=timezone.now().date()
    ).order_by('-date', '-time')
    
    context = {
        'upcoming_reservations': upcoming_reservations,
        'past_reservations': past_reservations,
    }
    
    return render(request, 'booking_system/my_reservations.html', context)

@login_required
def cancel_reservation(request, reservation_id):
    """Cancel a reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    # Check if cancellation is allowed (24 hours before)
    reservation_datetime = timezone.datetime.combine(reservation.date, reservation.time)
    if timezone.now() > reservation_datetime - timedelta(hours=24):
        messages.error(request, 'Cannot cancel within 24 hours of reservation.')
        return redirect('my_reservations')
    
    if reservation.status in ['confirmed', 'pending']:
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, 'Your reservation has been cancelled.')
    else:
        messages.error(request, 'This reservation cannot be cancelled.')
    
    return redirect('my_reservations')

@login_required
def add_review(request, restaurant_id):
    """Add a review for a restaurant"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check if user has completed reservation at this restaurant
    completed_reservations = Reservation.objects.filter(
        user=request.user,
        restaurant=restaurant,
        status='completed'
    )
    
    if not completed_reservations.exists():
        messages.error(request, 'You can only review restaurants where you have completed reservations.')
        return redirect('restaurant_detail', restaurant_id=restaurant_id)
    
    # Check if user already reviewed this restaurant
    existing_review = Review.objects.filter(user=request.user, restaurant=restaurant).first()
    if existing_review:
        messages.error(request, 'You have already reviewed this restaurant.')
        return redirect('restaurant_detail', restaurant_id=restaurant_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.restaurant = restaurant
            review.reservation = completed_reservations.first()  # Link to first completed reservation
            review.save()
            messages.success(request, 'Your review has been added!')
            return redirect('restaurant_detail', restaurant_id=restaurant_id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'restaurant': restaurant,
    }
    
    return render(request, 'booking_system/add_review.html', context)

def check_availability_view(request):
    """AJAX view to check table availability"""
    if request.method == 'GET':
        restaurant_id = request.GET.get('restaurant_id')
        date_str = request.GET.get('date')
        time_str = request.GET.get('time')
        guests = request.GET.get('guests')
        
        if not all([restaurant_id, date_str, time_str, guests]):
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id, is_active=True)
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            time = datetime.strptime(time_str, '%H:%M').time()
            guests = int(guests)
        except (Restaurant.DoesNotExist, ValueError):
            return JsonResponse({'error': 'Invalid parameters'}, status=400)
        
        # Check availability
        available_tables = Table.objects.filter(
            restaurant=restaurant,
            capacity__gte=guests,
            is_active=True
        ).exclude(
            reservations__date=date,
            reservations__time=time,
            reservations__status__in=['confirmed', 'pending']
        )
        
        return JsonResponse({
            'available': available_tables.exists(),
            'count': available_tables.count(),
            'message': f"{'Available' if available_tables.exists() else 'Not available'} for {guests} guests"
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def search_restaurants(request):
    """Search restaurants by name, cuisine, or location"""
    query = request.GET.get('q', '').strip()
    cuisine = request.GET.get('cuisine', '')
    location = request.GET.get('location', '')
    
    restaurants = Restaurant.objects.filter(is_active=True)
    
    if query:
        restaurants = restaurants.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if cuisine:
        restaurants = restaurants.filter(cuisine=cuisine)
    
    if location:
        restaurants = restaurants.filter(location__icontains=location)
    
    # Add rating and review count
    restaurants = restaurants.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating', '-review_count')
    
    # Pagination
    paginator = Paginator(restaurants, 12)
    page_number = request.GET.get('page')
    page_restaurants = paginator.get_page(page_number)
    
    context = {
        'restaurants': page_restaurants,
        'query': query,
        'cuisine': cuisine,
        'location': location,
        'total_results': restaurants.count(),
    }
    
    return render(request, 'booking_system/search_results.html', context)
