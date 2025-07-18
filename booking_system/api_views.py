from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta

from .models import Restaurant, Reservation, Review, Table
from .serializers import (
    RestaurantSerializer, ReservationSerializer, ReviewSerializer,
    TableSerializer, AvailabilitySerializer, DashboardStatsSerializer
)
from .filters import RestaurantFilter

class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for restaurants.
    
    Provides list and detail views for restaurants with filtering,
    searching, and ordering capabilities.
    """
    queryset = Restaurant.objects.filter(is_active=True)
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RestaurantFilter
    search_fields = ['name', 'location', 'cuisine']
    ordering_fields = ['name', 'rating', 'created_at']
    ordering = ['-rating']

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured restaurants (top-rated)"""
        featured = self.queryset.order_by('-rating')[:6]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def cuisines(self, request):
        """Get list of available cuisines"""
        cuisines = self.queryset.values_list('cuisine', flat=True).distinct()
        return Response({'cuisines': list(cuisines)})

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Check availability for a specific restaurant on a given date"""
        restaurant = self.get_object()
        date_str = request.query_params.get('date')
        
        if not date_str:
            return Response(
                {'error': 'Date parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get time slots with availability
        time_slots = []
        for hour in range(9, 23):  # 9 AM to 10 PM
            for minute in [0, 30]:
                slot_time = f"{hour:02d}:{minute:02d}"
                time_obj = datetime.strptime(slot_time, '%H:%M').time()
                
                # Count available tables for this time slot
                booked_tables = Reservation.objects.filter(
                    restaurant=restaurant,
                    date=date,
                    time=time_obj,
                    status__in=['confirmed', 'pending']
                ).count()
                
                total_tables = restaurant.tables.count()
                available_tables = total_tables - booked_tables
                
                time_slots.append({
                    'time': slot_time,
                    'available_tables': available_tables,
                    'is_available': available_tables > 0
                })
        
        return Response({
            'restaurant': restaurant.name,
            'date': date_str,
            'time_slots': time_slots
        })

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get reviews for a specific restaurant"""
        restaurant = self.get_object()
        reviews = restaurant.reviews.all().order_by('-created_at')
        
        # Pagination
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)

class ReservationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for reservations.
    
    Allows users to create, view, update, and cancel their reservations.
    """
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Reservation.objects.all()
        return Reservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Find available table
        restaurant_id = serializer.validated_data['restaurant_id']
        restaurant = Restaurant.objects.get(id=restaurant_id)
        date = serializer.validated_data['date']
        time = serializer.validated_data['time']
        guests = serializer.validated_data['number_of_guests']
        
        available_tables = Table.objects.filter(
            restaurant=restaurant,
            capacity__gte=guests,
            is_active=True
        ).exclude(
            reservations__date=date,
            reservations__time=time,
            reservations__status__in=['confirmed', 'pending']
        )
        
        if not available_tables.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("No tables available for the selected time")
        
        serializer.save(
            user=self.request.user,
            restaurant=restaurant,
            table=available_tables.first()
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a reservation"""
        reservation = self.get_object()
        
        if reservation.status == 'cancelled':
            return Response(
                {'error': 'Reservation is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if cancellation is allowed (24 hours before)
        reservation_datetime = timezone.datetime.combine(
            reservation.date, reservation.time
        )
        if timezone.now() > reservation_datetime - timedelta(hours=24):
            return Response(
                {'error': 'Cannot cancel within 24 hours of reservation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'cancelled'
        reservation.save()
        
        return Response({'message': 'Reservation cancelled successfully'})

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming reservations for the user"""
        upcoming = self.get_queryset().filter(
            date__gte=timezone.now().date(),
            status__in=['confirmed', 'pending']
        ).order_by('date', 'time')
        
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get reservation history for the user"""
        history = self.get_queryset().filter(
            date__lt=timezone.now().date()
        ).order_by('-date', '-time')
        
        page = self.paginate_queryset(history)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for reviews.
    
    Allows users to create, view, update, and delete their reviews.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Review.objects.all()
        return Review.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        restaurant_id = serializer.validated_data['restaurant_id']
        restaurant = Restaurant.objects.get(id=restaurant_id)
        
        # Check if user already reviewed this restaurant
        existing_review = Review.objects.filter(
            user=self.request.user,
            restaurant=restaurant
        ).first()
        
        if existing_review:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You have already reviewed this restaurant")
        
        serializer.save(user=self.request.user, restaurant=restaurant)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_availability(request):
    """
    Check table availability for specific criteria.
    
    Expected parameters:
    - restaurant_id: UUID of the restaurant
    - date: Date in YYYY-MM-DD format
    - time: Time in HH:MM format
    - guests: Number of guests (integer)
    """
    serializer = AvailabilitySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        restaurant = Restaurant.objects.get(id=data['restaurant_id'], is_active=True)
    except Restaurant.DoesNotExist:
        return Response(
            {'error': 'Restaurant not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Find available tables
    available_tables = Table.objects.filter(
        restaurant=restaurant,
        capacity__gte=data['guests'],
        is_active=True
    ).exclude(
        reservations__date=data['date'],
        reservations__time=data['time'],
        reservations__status__in=['confirmed', 'pending']
    )
    
    table_serializer = TableSerializer(available_tables, many=True)
    
    return Response({
        'available': available_tables.exists(),
        'available_tables': table_serializer.data,
        'count': available_tables.count(),
        'restaurant': restaurant.name,
        'requested_date': data['date'].isoformat(),
        'requested_time': data['time'].strftime('%H:%M'),
        'requested_guests': data['guests']
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for the authenticated user.
    
    Returns different data based on user role:
    - Regular users: Personal reservation statistics
    - Staff users: Overall system statistics
    """
    if request.user.is_staff:
        # Admin dashboard stats
        today = timezone.now().date()
        
        stats = {
            'total_restaurants': Restaurant.objects.filter(is_active=True).count(),
            'total_reservations': Reservation.objects.count(),
            'today_reservations': Reservation.objects.filter(date=today).count(),
            'pending_reservations': Reservation.objects.filter(status='pending').count(),
            'total_users': Reservation.objects.values('user').distinct().count(),
            'popular_cuisines': list(
                Restaurant.objects.values('cuisine')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            ),
            'recent_reviews': ReviewSerializer(
                Review.objects.order_by('-created_at')[:5],
                many=True,
                context={'request': request}
            ).data
        }
    else:
        # User dashboard stats
        user_reservations = Reservation.objects.filter(user=request.user)
        
        stats = {
            'total_reservations': user_reservations.count(),
            'upcoming_reservations': user_reservations.filter(
                date__gte=timezone.now().date(),
                status__in=['confirmed', 'pending']
            ).count(),
            'completed_reservations': user_reservations.filter(
                status='completed'
            ).count(),
            'cancelled_reservations': user_reservations.filter(
                status='cancelled'
            ).count(),
            'favorite_restaurants': list(
                user_reservations.values('restaurant__name', 'restaurant__id')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            ),
            'recent_reservations': ReservationSerializer(
                user_reservations.order_by('-created_at')[:5],
                many=True,
                context={'request': request}
            ).data
        }
    
    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)

@api_view(['GET'])
def api_health(request):
    """API health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })
