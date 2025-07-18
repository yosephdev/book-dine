from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Restaurant, Table, Reservation, Review

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'table', 'date', 'time', 'number_of_guests',
            'dietary_restrictions', 'childs_chair', 'special_requests',
            'contact_phone', 'contact_email'
        ]
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'min': timezone.now().date().isoformat()
                }
            ),
            'time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control'
                }
            ),
            'number_of_guests': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1,
                    'max': 20
                }
            ),
            'dietary_restrictions': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Any dietary restrictions or allergies?'
                }
            ),
            'special_requests': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Any special requests?'
                }
            ),
            'contact_phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '+1234567890'
                }
            ),
            'contact_email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'your.email@example.com'
                }
            ),
            'childs_chair': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.restaurant = kwargs.pop('restaurant', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.restaurant:
            self.fields['table'].queryset = Table.objects.filter(
                restaurant=self.restaurant,
                is_active=True,
                status='available'
            )
            self.fields['table'].widget.attrs.update({'class': 'form-control'})
        
        # Set default contact info from user
        if self.user and not self.instance.pk:
            self.fields['contact_email'].initial = self.user.email
            if hasattr(self.user, 'phone'):
                self.fields['contact_phone'].initial = self.user.phone

    def clean_date(self):
        booking_date = self.cleaned_data.get('date')
        if booking_date < timezone.now().date():
            raise ValidationError('Booking date cannot be in the past.')
        
        # Don't allow bookings more than 3 months in advance
        max_date = timezone.now().date() + timedelta(days=90)
        if booking_date > max_date:
            raise ValidationError('Bookings can only be made up to 3 months in advance.')
        
        return booking_date

    def clean_time(self):
        booking_time = self.cleaned_data.get('time')
        booking_date = self.cleaned_data.get('date')
        
        if booking_date == timezone.now().date():
            current_time = timezone.now().time()
            if booking_time <= current_time:
                raise ValidationError('Booking time must be in the future.')
        
        # Check restaurant operating hours
        if self.restaurant:
            if booking_time < self.restaurant.opening_time or booking_time > self.restaurant.closing_time:
                raise ValidationError(
                    f'Restaurant is open from {self.restaurant.opening_time} to {self.restaurant.closing_time}.'
                )
        
        return booking_time

    def clean(self):
        cleaned_data = super().clean()
        table = cleaned_data.get('table')
        reservation_date = cleaned_data.get('date')
        reservation_time = cleaned_data.get('time')
        number_of_guests = cleaned_data.get('number_of_guests')

        if table and reservation_date and reservation_time:
            # Check table capacity
            if number_of_guests and number_of_guests > table.capacity:
                raise ValidationError({
                    'number_of_guests': f'This table can accommodate maximum {table.capacity} guests.'
                })
            
            # Check table availability
            duration = timedelta(hours=2)
            if not table.is_available(reservation_date, reservation_time, duration):
                raise ValidationError({
                    'table': 'The selected table is not available for the chosen date and time.'
                })

        return cleaned_data

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-check-input'}
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Share your experience...'
                }
            ),
        }

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if len(comment.strip()) < 10:
            raise ValidationError('Please provide a more detailed review (at least 10 characters).')
        return comment

class RestaurantFilterForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        label='Search',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Search restaurants...'
            }
        )
    )
    cuisine = forms.ChoiceField(
        choices=[],
        required=False,
        label='Cuisine',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    rating = forms.ChoiceField(
        choices=[(i, f'{i}+ Stars') for i in range(1, 6)],
        required=False,
        label='Minimum Rating',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    location = forms.CharField(
        max_length=100,
        required=False,
        label='Location',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter location...'
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cuisines = Restaurant.objects.values_list('cuisine', flat=True).distinct()
        self.fields['cuisine'].choices = [('', 'All Cuisines')] + [
            (c, c.title()) for c in cuisines if c
        ]

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            'name', 'location', 'cuisine', 'description',
            'phone', 'email', 'website', 'image',
            'opening_time', 'closing_time'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'cuisine': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['table_number', 'capacity', 'status']
        widgets = {
            'table_number': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
