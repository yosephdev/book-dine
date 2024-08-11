from django import forms
from django.core.exceptions import ValidationError
from .models import Reservation, Table, Review
from datetime import date as today_date


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['table', 'date', 'time', 'number_of_guests',
                  'dietary_restrictions', 'childs_chair', 'special_requests']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        if restaurant:
            self.fields['table'].queryset = Table.objects.filter(
                restaurant=restaurant)

    def clean_date(self):
        booking_date = self.cleaned_data.get('date')
        if booking_date < today_date.today():
            raise ValidationError('The booking date cannot be in the past.')
        return booking_date

    def clean_number_of_guests(self):
        number_of_guests = self.cleaned_data.get('number_of_guests')
        if number_of_guests <= 0:
            raise ValidationError(
                'The number of guests must be a positive number.')
        return number_of_guests


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
