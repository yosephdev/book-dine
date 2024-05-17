from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Restaurant, Table, Reservation, Review

# Create your tests here.


class RestaurantModelTest(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            location='Test Location',
            cuisine='Test Cuisine',
            rating=4.5
        )

    def test_restaurant_str(self):
        self.assertEqual(str(self.restaurant), 'Test Restaurant')


class TableModelTest(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            location='Test Location',
            cuisine='Test Cuisine',
            rating=4.5
        )
        self.table = Table.objects.create(
            restaurant=self.restaurant,
            capacity=4,
            table_number=1,
            status='available'
        )

    def test_table_str(self):
        self.assertEqual(str(self.table), 'Table 1 (4 seats)')

    def test_table_is_available(self):
        date = timezone.now().date()
        start_time = timezone.now().time()
        duration = timezone.timedelta(hours=2)
        self.assertTrue(self.table.is_available(date, start_time, duration))


class ReservationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            location='Test Location',
            cuisine='Test Cuisine',
            rating=4.5
        )
        self.table = Table.objects.create(
            restaurant=self.restaurant,
            capacity=4,
            table_number=1,
            status='available'
        )
        self.reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=timezone.now().date(),
            time=timezone.now().time(),
            number_of_guests=2
        )

    def test_reservation_str(self):
        expected_str = f"Reservation for {self.user.username} on {self.reservation.date} at {self.reservation.time}"
        self.assertEqual(str(self.reservation), expected_str)


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            location='Test Location',
            cuisine='Test Cuisine',
            rating=4.5
        )
        self.review = Review.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            rating=5,
            comment='Great restaurant!'
        )

    def test_review_str(self):
        expected_str = f"Review by {self.user.username} for {self.restaurant.name}"
        self.assertEqual(str(self.review), expected_str)


class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            location='Test Location',
            cuisine='Test Cuisine',
            rating=4.5
        )

    def test_home_view(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_system/home.html')


def test_restaurant_detail_view(self):
    url = reverse('restaurant_detail', args=[self.restaurant.id])
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'booking_system/restaurant_detail.html')
    self.assertContains(response, self.restaurant.name)


def test_make_reservation_view(self):
    url = reverse('make_reservation')
    self.client.login(username='testuser', password='testpassword')
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'booking_system/make_reservation.html')

    # Test POST request with valid form data
    table = Table.objects.create(
        restaurant=self.restaurant,
        capacity=4,
        table_number=1,
        status='available'
    )
    form_data = {
        'table': table.id,
        'date': timezone.now().date(),
        'time': timezone.now().time(),
        'number_of_guests': 2
    }
    response = self.client.post(url, data=form_data)
    # Redirect after successful reservation
    self.assertEqual(response.status_code, 302)
    self.assertEqual(Reservation.objects.count(), 1)


def test_view_reservations_view(self):
    url = reverse('view_reservations')
    self.client.login(username='testuser', password='testpassword')
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'booking_system/view_reservations.html')


def test_write_review_view(self):
    url = reverse('write_review', args=[self.restaurant.id])
    self.client.login(username='testuser', password='testpassword')
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'booking_system/write_review.html')

    # Test POST request with valid form data
    form_data = {
        'rating': 5,
        'comment': 'Great restaurant!'
    }
    response = self.client.post(url, data=form_data)
    # Redirect after successful review submission
    self.assertEqual(response.status_code, 302)
    self.assertEqual(Review.objects.count(), 1)
