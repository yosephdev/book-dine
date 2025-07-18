from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from django.utils import timezone
from datetime import datetime, timedelta, time
import random

from booking_system.models import Restaurant, Table, Reservation, Review

class Command(BaseCommand):
    help = 'Create sample data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--restaurants',
            type=int,
            default=10,
            help='Number of restaurants to create'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create'
        )
        parser.add_argument(
            '--reservations',
            type=int,
            default=200,
            help='Number of reservations to create'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create or get a restaurant owner user
        owner, created = CustomUser.objects.get_or_create(
            username='restaurant_owner',
            defaults={
                'email': 'owner@bookdine.com',
                'first_name': 'Restaurant',
                'last_name': 'Owner',
                'role': CustomUser.RESTAURANT_OWNER
            }
        )
        if created:
            owner.set_password('password123')
            owner.save()
        
        # Create sample restaurants
        restaurants = self.create_restaurants(options['restaurants'], owner)
        self.stdout.write(f'Created {len(restaurants)} restaurants')
        
        # Create sample users
        users = self.create_users(options['users'])
        self.stdout.write(f'Created {len(users)} users')
        
        # Create tables for restaurants
        self.create_tables(restaurants)
        self.stdout.write('Created tables for restaurants')
        
        # Create sample reservations
        reservations = self.create_reservations(restaurants, users, options['reservations'])
        self.stdout.write(f'Created {len(reservations)} reservations')
        
        # Create sample reviews
        reviews = self.create_reviews(restaurants, users)
        self.stdout.write(f'Created {len(reviews)} reviews')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )

    def create_restaurants(self, count, owner):
        restaurants = []
        cuisines = ['italian', 'french', 'japanese', 'mexican', 'indian', 'chinese', 'american', 'mediterranean']
        locations = ['Downtown', 'Midtown', 'Uptown', 'Westside', 'Eastside', 'Northside', 'Southside']
        
        restaurant_names = [
            'The Golden Spoon', 'Bella Vista', 'Sakura Garden', 'El Mariachi',
            'Spice Palace', 'Dragon House', 'Liberty Grill', 'Olive Branch',
            'Sunset Bistro', 'The Copper Pot', 'Moonlight Diner', 'Harbor View',
            'Mountain Peak', 'City Lights', 'Garden Terrace', 'The Wine Cellar'
        ]
        
        for i in range(count):
            restaurant = Restaurant.objects.create(
                name=random.choice(restaurant_names) + f' #{i+1}',
                description=f'A wonderful {random.choice(cuisines).lower()} restaurant with excellent service.',
                cuisine=random.choice(cuisines),
                location=random.choice(locations),
                phone=f'+1{random.randint(2000000000, 9999999999)}',
                email=f'restaurant{i+1}@example.com',
                opening_time=time(9, 0),
                closing_time=time(23, 0),
                is_active=True,
                user=owner,
                rating=round(random.uniform(3.5, 5.0), 1)
            )
            restaurants.append(restaurant)
        
        return restaurants

    def create_users(self, count):
        users = []
        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Tom', 'Emma', 'Chris', 'Anna']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f'{first_name.lower()}.{last_name.lower()}{i+1}'
            
            user = CustomUser.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='testpass123',
                first_name=first_name,
                last_name=last_name,
                role=CustomUser.CUSTOMER
            )
            users.append(user)
        
        return users

    def create_tables(self, restaurants):
        for restaurant in restaurants:
            # Create tables with different capacities
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
                        table_number=str(table_number),
                        capacity=capacity,
                        status='available',
                        is_active=True
                    )
                    table_number += 1

    def create_reservations(self, restaurants, users, count):
        reservations = []
        statuses = ['confirmed', 'pending']
        status_weights = [0.8, 0.2]  # Probability weights
        
        # Create reservations for the next 60 days (future dates only)
        start_date = timezone.now().date()
        end_date = timezone.now().date() + timedelta(days=60)
        
        for i in range(count):
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
                
                # Determine status based on date
                if reservation_date < timezone.now().date():
                    status = random.choices(['completed', 'cancelled'], weights=[0.8, 0.2])[0]
                else:
                    status = random.choices(statuses, weights=status_weights)[0]
                
                reservation = Reservation.objects.create(
                    user=user,
                    restaurant=restaurant,
                    table=table,
                    date=reservation_date,
                    time=reservation_time,
                    number_of_guests=party_size,
                    status=status,
                    special_requests=random.choice([
                        '', 'Window seat please', 'Birthday celebration',
                        'Anniversary dinner', 'Quiet table', 'High chair needed'
                    ])
                )
                reservations.append(reservation)
        
        return reservations

    def create_reviews(self, restaurants, users):
        reviews = []
        
        # Create reviews for completed reservations
        completed_reservations = Reservation.objects.filter(status='completed')
        
        # Only create reviews for about 60% of completed reservations
        reservations_to_review = random.sample(
            list(completed_reservations),
            min(int(len(completed_reservations) * 0.6), len(completed_reservations))
        )
        
        review_comments = [
            'Excellent food and service!',
            'Great atmosphere, will definitely come back.',
            'Food was good but service was slow.',
            'Amazing experience, highly recommended!',
            'Decent food, nothing special.',
            'Outstanding meal and wonderful staff.',
            'Good value for money.',
            'The ambiance was perfect for our date night.',
            'Food was delicious but a bit pricey.',
            'Service was exceptional, food was okay.'
        ]
        
        for reservation in reservations_to_review:
            # Random rating (weighted towards higher ratings)
            rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.15, 0.35, 0.35])[0]
            
            review = Review.objects.create(
                user=reservation.user,
                restaurant=reservation.restaurant,
                reservation=reservation,
                rating=rating,
                comment=random.choice(review_comments),
                created_at=reservation.date + timedelta(days=random.randint(1, 7))
            )
            reviews.append(review)
        
        return reviews