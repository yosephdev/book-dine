#!/usr/bin/env python
"""
Script to populate the database with sample data for development and testing.
Run this script from the project root directory:
python scripts/populate_sample_data.py
"""

import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BookDine.settings')
django.setup()

from accounts.models import CustomUser
from django.utils import timezone
from datetime import datetime, timedelta, time
import random

from booking_system.models import Restaurant, Table, Reservation, Review

def create_sample_data():
    print("🚀 Creating sample data for BookDine...")
    
    # Create or get a default user for restaurants
    user, created = CustomUser.objects.get_or_create(
        username='restaurant_owner',
        defaults={
            'email': 'owner@bookdine.com',
            'first_name': 'Restaurant',
            'last_name': 'Owner',
            'role': CustomUser.RESTAURANT_OWNER
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f"✅ Created user: {user.username}")
    
    # Create sample restaurants
    restaurants_data = [
        {
            'name': 'The Golden Spoon',
            'cuisine': 'italian',
            'location': 'Downtown',
            'description': 'Authentic Italian cuisine with a modern twist. Fresh pasta made daily.',
            'phone': '+1234567890',
            'email': 'info@goldenspoon.com',
        },
        {
            'name': 'Sakura Garden',
            'cuisine': 'japanese',
            'location': 'Midtown',
            'description': 'Traditional Japanese dining experience with fresh sushi and sashimi.',
            'phone': '+1234567891',
            'email': 'hello@sakuragarden.com',
        },
        {
            'name': 'El Mariachi',
            'cuisine': 'mexican',
            'location': 'Westside',
            'description': 'Vibrant Mexican restaurant with authentic flavors and live music.',
            'phone': '+1234567892',
            'email': 'contact@elmariachi.com',
        },
        {
            'name': 'Spice Palace',
            'cuisine': 'indian',
            'location': 'Eastside',
            'description': 'Aromatic Indian dishes with traditional spices and modern presentation.',
            'phone': '+1234567893',
            'email': 'info@spicepalace.com',
        },
        {
            'name': 'Bella Vista',
            'cuisine': 'mediterranean',
            'location': 'Uptown',
            'description': 'Mediterranean cuisine with fresh ingredients and beautiful ambiance.',
            'phone': '+1234567894',
            'email': 'hello@bellavista.com',
        }
    ]
    
    restaurants = []
    for data in restaurants_data:
        restaurant, created = Restaurant.objects.get_or_create(
            name=data['name'],
            defaults={
                **data,
                'opening_time': time(9, 0),
                'closing_time': time(23, 0),
                'is_active': True,
                'rating': round(random.uniform(3.5, 5.0), 1),
                'user': user
            }
        )
        restaurants.append(restaurant)
        if created:
            print(f"✅ Created restaurant: {restaurant.name}")
    
    # Create tables for each restaurant
    for restaurant in restaurants:
        if not restaurant.tables.exists():
            # Create different table configurations
            table_configs = [
                (2, 4),  # 4 tables for 2 people
                (4, 6),  # 6 tables for 4 people
                (6, 3),  # 3 tables for 6 people
                (8, 2),  # 2 tables for 8 people
            ]
            
            table_number = 1
            for capacity, count in table_configs:
                for _ in range(count):
                    Table.objects.create(
                        restaurant=restaurant,
                        table_number=table_number,
                        capacity=capacity,
                        is_active=True
                    )
                    table_number += 1
            
            print(f"✅ Created {table_number - 1} tables for {restaurant.name}")
    
    # Create sample users
    sample_users = [
        {'username': 'john.doe', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'},
        {'username': 'jane.smith', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com'},
        {'username': 'mike.johnson', 'first_name': 'Mike', 'last_name': 'Johnson', 'email': 'mike@example.com'},
        {'username': 'sarah.wilson', 'first_name': 'Sarah', 'last_name': 'Wilson', 'email': 'sarah@example.com'},
        {'username': 'david.brown', 'first_name': 'David', 'last_name': 'Brown', 'email': 'david@example.com'},
    ]
    
    users = []
    for user_data in sample_users:
        user, created = CustomUser.objects.get_or_create(
            username=user_data['username'],
            defaults={
                **user_data,
                'password': 'pbkdf2_sha256$600000$dummy$dummy',  # Dummy password hash
                'role': CustomUser.CUSTOMER
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"✅ Created user: {user.username}")
        users.append(user)
    
    # Create sample reservations
    print("📅 Creating sample reservations...")
    
    # Create reservations for the next 60 days (future dates only)
    start_date = timezone.now().date()
    end_date = timezone.now().date() + timedelta(days=60)
    
    reservation_count = 0
    for _ in range(100):  # Create 100 reservations
        restaurant = random.choice(restaurants)
        user = random.choice(users)
        
        # Random date within range
        random_days = random.randint(0, (end_date - start_date).days)
        reservation_date = start_date + timedelta(days=random_days)
        
        # Random time (9 AM to 10 PM)
        hour = random.randint(9, 22)
        minute = random.choice([0, 30])
        reservation_time = datetime.strptime(f'{hour}:{minute:02d}', '%H:%M').time()
        
        # Random party size
        party_size = random.choices([2, 4, 6, 8], weights=[0.4, 0.4, 0.15, 0.05])[0]
        
        # Get available table
        available_tables = restaurant.tables.filter(
            capacity__gte=party_size
        ).exclude(
            reservations__date=reservation_date,
            reservations__time=reservation_time,
            reservations__status__in=['confirmed', 'pending']
        )
        
        if available_tables.exists():
            table = available_tables.first()
            
            # All reservations are future, so set appropriate status
            status = random.choices(['confirmed', 'pending'], weights=[0.8, 0.2])[0]
            
            reservation, created = Reservation.objects.get_or_create(
                user=user,
                restaurant=restaurant,
                table=table,
                date=reservation_date,
                time=reservation_time,
                defaults={
                    'number_of_guests': party_size,
                    'status': status,
                    'special_requests': random.choice([
                        '', 'Window seat please', 'Birthday celebration',
                        'Anniversary dinner', 'Quiet table'
                    ])
                }
            )
            
            if created:
                reservation_count += 1
    
    print(f"✅ Created {reservation_count} reservations")
    
    # Create sample reviews
    print("⭐ Creating sample reviews...")
    
    completed_reservations = Reservation.objects.filter(status='completed')
    review_count = 0
    
    review_comments = [
        'Excellent food and service! Will definitely come back.',
        'Great atmosphere and delicious meals.',
        'Outstanding experience, highly recommended!',
        'Good food but service could be improved.',
        'Amazing dinner, perfect for special occasions.',
        'Fresh ingredients and wonderful presentation.',
        'Great value for money.',
        'The staff was very friendly and accommodating.',
    ]
    
    for reservation in completed_reservations[:50]:  # Create reviews for first 50 completed reservations
        if not hasattr(reservation, 'review'):  # Check if review doesn't exist
            rating = random.choices([3, 4, 5], weights=[0.2, 0.4, 0.4])[0]
            
            review, created = Review.objects.get_or_create(
                user=reservation.user,
                restaurant=reservation.restaurant,
                reservation=reservation,
                defaults={
                    'rating': rating,
                    'comment': random.choice(review_comments),
                }
            )
            
            if created:
                review_count += 1
    
    print(f"✅ Created {review_count} reviews")
    
    print("\n🎉 Sample data creation completed!")
    print("\n📊 Summary:")
    print(f"   • Restaurants: {Restaurant.objects.count()}")
    print(f"   • Tables: {Table.objects.count()}")
    print(f"   • Users: {CustomUser.objects.count()}")
    print(f"   • Reservations: {Reservation.objects.count()}")
    print(f"   • Reviews: {Review.objects.count()}")
    
    print("\n🔗 You can now test the API endpoints:")
    print("   • API Root: http://localhost:8000/api/")
    print("   • Restaurants: http://localhost:8000/api/restaurants/")
    print("   • Reservations: http://localhost:8000/api/reservations/")
    print("   • Reviews: http://localhost:8000/api/reviews/")
    print("   • API Docs: http://localhost:8000/api/docs/")
    print("   • Admin: http://localhost:8000/admin/")

if __name__ == '__main__':
    create_sample_data()