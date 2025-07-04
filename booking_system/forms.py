from django import forms
from django.core.exceptions import ValidationError
from .models import Reservation, Table, Review
from datetime import date as today_date
from django.utils import timezone


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
        self.restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        if self.restaurant:
            self.fields['table'].queryset = Table.objects.filter(
                restaurant=self.restaurant)

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

    def clean(self):
        cleaned_data = super().clean()
        table = cleaned_data.get('table')
        reservation_date = cleaned_data.get('date')
        reservation_time = cleaned_data.get('time')

        if table and reservation_date and reservation_time:
            duration = timezone.timedelta(hours=2)
            if table.restaurant != self.restaurant:
                raise ValidationError(
                    {'table': 'Invalid table selection for this restaurant.'})
            if not table.is_available(reservation_date, reservation_time, duration):
                raise ValidationError(
                    {'table': 'The selected table is not available for the chosen date and time.'})

        return cleaned_data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
