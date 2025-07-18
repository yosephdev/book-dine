from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import time, timedelta
from booking_system.models import Restaurant, Table, Reservation, Review

User = get_user_model()

class RestaurantModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testowner',
            email='owner@test.com',
            password='testpass123'
        )
        
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            location='Test City',
            cuisine='italian',
            description='A test restaurant',
            rating=4.5,
            phone='+1234567890',
            email='restaurant@test.com',
            user=self.user,
            opening_time=time(9, 0),
            closing_time=time(22, 0)
        )

    def test_restaurant_creation(self):
        """Test restaurant is created correctly"""
        self.assertEqual(self.restaurant.name, 'Test Restaurant')
        self.assertEqual(self.restaurant.cuisine, 'italian')
        self.assertEqual(self.restaurant.user, self.user)
        self.assertTrue(self.restaurant.is_active)

    def test_restaurant_str_method(self):
        """Test restaurant string representation"""
        self.assertEqual(str(self.restaurant), 'Test Restaurant')

    def test_restaurant_clean_method(self):
        """Test restaurant validation"""
        # Valid times should not raise error
        self.restaurant.clean()
        
        # Invalid times should raise error
        self.restaurant.opening_time = time(23, 0)
        self.restaurant.closing_time = time(22, 0)
        with self.assertRaises(ValidationError):
            self.restaurant.clean()

    def test_average_rating_property(self):
        """Test average rating calculation"""
        # No reviews initially
        self.assertEqual(self.restaurant.average_rating, 0)
        
        # Create test user for reviews
        reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@test.com',
            password='testpass123'
        )
        
        # Add reviews
        Review.objects.create(
            user=reviewer,
            restaurant=self.restaurant,
            rating=4,
            comment='Good food'
        )
        
        # Check average rating
        self.assertEqual(self.restaurant.average_rating, 4.0)

class TableModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testowner',
            email='owner@test.com',
            password='testpass123'
        )
        
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            location='Test City',
            cuisine='italian',
            user=self.user
        )
        
        self.table = Table.objects.create(
            restaurant=self.restaurant,
            table_number='T1',
            capacity=4,
            status='available'
        )

    def test_table_creation(self):
        """Test table is created correctly"""
        self.assertEqual(self.table.table_number, 'T1')
        self.assertEqual(self.table.capacity, 4)
        self.assertEqual(self.table.restaurant, self.restaurant)
        self.assertTrue(self.table.is_active)

    def test_table_str_method(self):
        """Test table string representation"""
        expected = f"Table T1 at {self.restaurant.name}"
        self.assertEqual(str(self.table), expected)

    def test_table_availability(self):
        """Test table availability checking"""
        test_date = timezone.now().date() + timedelta(days=1)
        test_time = time(19, 0)
        
        # Table should be available initially
        self.assertTrue(self.table.is_available(test_date, test_time))
        
        # Create a reservation
        customer = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            password='testpass123'
        )
        
        Reservation.objects.create(
            user=customer,
            restaurant=self.restaurant,
            table=self.table,
            date=test_date,
            time=test_time,
            start_time=test_time,
            end_time=time(21, 0),
            number_of_guests=2,
            status='confirmed'
        )
        
        # Table should not be available now
        self.assertFalse(self.table.is_available(test_date, test_time))

class ReservationModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@test.com',
            password='testpass123'
        )
        
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            password='testpass123'
        )
        
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            location='Test City',
            cuisine='italian',
            user=self.owner
        )
        
        self.table = Table.objects.create(
            restaurant=self.restaurant,
            table_number='T1',
            capacity=4
        )

    def test_reservation_creation(self):
        """Test reservation is created correctly"""
        future_date = timezone.now().date() + timedelta(days=1)
        
        reservation = Reservation.objects.create(
            user=self.customer,
            restaurant=self.restaurant,
            table=self.table,
            date=future_date,
            time=time(19, 0),
            number_of_guests=2
        )
        
        self.assertEqual(reservation.user, self.customer)
        self.assertEqual(reservation.restaurant, self.restaurant)
        self.assertEqual(reservation.table, self.table)
        self.assertEqual(reservation.status, 'pending')

    def test_reservation_clean_method(self):
        """Test reservation validation"""
        # Past date should raise error
        past_date = timezone.now().date() - timedelta(days=1)
        
        reservation = Reservation(
            user=self.customer,
            restaurant=self.restaurant,
            table=self.table,
            date=past_date,
            time=time(19, 0),
            number_of_guests=2
        )
        
        with self.assertRaises(ValidationError):
            reservation.clean()

    def test_reservation_save_method(self):
        """Test reservation save method sets default times"""
        future_date = timezone.now().date() + timedelta(days=1)
        
        reservation = Reservation.objects.create(
            user=self.customer,
            restaurant=self.restaurant,
            table=self.table,
            date=future_date,
            time=time(19, 0),
            number_of_guests=2
        )
        
        # start_time should be set to time
        self.assertEqual(reservation.start_time, reservation.time)
        
        # end_time should be set to 2 hours later
        expected_end_time = time(21, 0)
        self.assertEqual(reservation.end_time, expected_end_time)

    def test_can_be_cancelled_property(self):
        """Test cancellation logic"""
        # Future reservation should be cancellable
        future_date = timezone.now().date() + timedelta(days=1)
        
        reservation = Reservation.objects.create(
            user=self.customer,
            restaurant=self.restaurant,
            table=self.table,
            date=future_date,
            time=time(19, 0),
            number_of_guests=2,
            status='confirmed'
        )
        
        self.assertTrue(reservation.can_be_cancelled)
        
        # Completed reservation should not be cancellable
        reservation.status = 'completed'
        reservation.save()
        self.assertFalse(reservation.can_be_cancelled)

class ReviewModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@test.com',
            password='testpass123'
        )
        
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            password='testpass123'
        )
        
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            location='Test City',
            cuisine='italian',
            user=self.owner
        )

    def test_review_creation(self):
        """Test review is created correctly"""
        review = Review.objects.create(
            user=self.customer,
            restaurant=self.restaurant,
            rating=5,
            comment='Excellent food and service!'
        )
        
        self.assertEqual(review.user, self.customer)
        self.assertEqual(review.restaurant, self.restaurant)
        self.assertEqual(review.rating, 5)
        self.assertFalse(review.is_verified)

    def test_review_str_method(self):
        """Test review string representation"""
        review = Review.objects.create(
            user=self.customer,
            restaurant=self.restaurant,
            rating=4,
            comment='Good food'
        )
        
        expected = f"{self.customer.username} - {self.restaurant.name} (4/5)"
        self.assertEqual(str(review), expected)

    def test_unique_together_constraint(self):
        """Test that user can only review a restaurant once"""
        Review.objects.create(
            user=self.customer,
            restaurant=self.restaurant,
            rating=5,
            comment='Great!'
        )
        
        # Second review from same user should raise error
        with self.assertRaises(Exception):
            Review.objects.create(
                user=self.customer,
                restaurant=self.restaurant,
                rating=3,
                comment='Changed my mind'
            )