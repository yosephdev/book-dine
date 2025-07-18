from rest_framework import serializers
from accounts.models import CustomUser
from .models import Restaurant, Table, Reservation, Review

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'phone_number']
        read_only_fields = ['id']

class RestaurantSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    total_reviews = serializers.SerializerMethodField()
    is_open_now = serializers.SerializerMethodField()
    
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'location', 'cuisine', 'description',
            'rating', 'average_rating', 'total_reviews', 'phone', 
            'email', 'website', 'image', 'opening_time', 'closing_time', 
            'is_active', 'is_open_now', 'created_at'
        ]
    
    def get_total_reviews(self, obj):
        return obj.reviews.count()
    
    def get_is_open_now(self, obj):
        from django.utils import timezone
        now = timezone.now().time()
        return obj.opening_time <= now <= obj.closing_time

class TableSerializer(serializers.ModelSerializer):
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = Table
        fields = ['id', 'table_number', 'capacity', 'status', 'is_active', 'is_available']
    
    def get_is_available(self, obj):
        # Check if table is available for current time
        from django.utils import timezone
        now = timezone.now()
        return not obj.reservations.filter(
            date=now.date(),
            time__lte=now.time(),
            status__in=['confirmed', 'pending']
        ).exists()

class ReservationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    restaurant_id = serializers.UUIDField(write_only=True)
    table = TableSerializer(read_only=True)
    can_cancel = serializers.SerializerMethodField()
    time_until_reservation = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'user', 'restaurant', 'restaurant_id', 'table', 'date', 'time',
            'number_of_guests', 'status', 'special_requests', 'can_cancel',
            'time_until_reservation', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'table', 'created_at', 'updated_at']
    
    def get_can_cancel(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        reservation_datetime = timezone.datetime.combine(obj.date, obj.time)
        return (
            obj.status in ['confirmed', 'pending'] and
            timezone.now() < reservation_datetime - timedelta(hours=24)
        )
    
    def get_time_until_reservation(self, obj):
        from django.utils import timezone
        
        reservation_datetime = timezone.datetime.combine(obj.date, obj.time)
        if timezone.now() < reservation_datetime:
            delta = reservation_datetime - timezone.now()
            return {
                'days': delta.days,
                'hours': delta.seconds // 3600,
                'minutes': (delta.seconds % 3600) // 60
            }
        return None
    
    def validate(self, data):
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        # Validate date is not in the past
        if data['date'] < timezone.now().date():
            raise serializers.ValidationError("Cannot book for past dates")
        
        # Validate time is not in the past for today's bookings
        if data['date'] == timezone.now().date():
            reservation_time = datetime.combine(data['date'], data['time'])
            if reservation_time < timezone.now():
                raise serializers.ValidationError("Cannot book for past times")
        
        # Validate number of guests
        if data['number_of_guests'] < 1 or data['number_of_guests'] > 20:
            raise serializers.ValidationError("Number of guests must be between 1 and 20")
        
        return data

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    restaurant_id = serializers.UUIDField(write_only=True)
    reservation_id = serializers.UUIDField(write_only=True, required=False)
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'restaurant', 'restaurant_id', 'reservation_id',
            'rating', 'comment', 'can_edit', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.user == request.user
        return False
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate(self, data):
        request = self.context.get('request')
        
        # Check if user has a completed reservation at this restaurant
        if request and request.user:
            from .models import Restaurant
            restaurant = Restaurant.objects.get(id=data['restaurant_id'])
            
            completed_reservations = Reservation.objects.filter(
                user=request.user,
                restaurant=restaurant,
                status='completed'
            )
            
            if not completed_reservations.exists():
                raise serializers.ValidationError(
                    "You can only review restaurants where you have completed reservations"
                )
        
        return data

class AvailabilitySerializer(serializers.Serializer):
    restaurant_id = serializers.UUIDField()
    date = serializers.DateField()
    time = serializers.TimeField()
    guests = serializers.IntegerField(min_value=1, max_value=20)
    
    def validate_date(self, value):
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("Cannot check availability for past dates")
        return value

class DashboardStatsSerializer(serializers.Serializer):
    total_reservations = serializers.IntegerField()
    upcoming_reservations = serializers.IntegerField()
    completed_reservations = serializers.IntegerField()
    favorite_restaurants = serializers.ListField()
    live_stats = serializers.DictField(required=False)
    booking_trends = serializers.DictField(required=False)
    customer_insights = serializers.DictField(required=False)
    revenue_analytics = serializers.DictField(required=False)
