from django import forms
from .models import Reservation, Review, Table


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'dietary_restrictions', 'childs_chair', 'table',
            'date', 'time', 'number_of_guests', 'special_requests'
        ]
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


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
