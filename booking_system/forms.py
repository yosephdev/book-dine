from django import forms
from .models import Reservation, Review


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['restaurant', 'date', 'time', 'number_of_guests', 'dietary_restrictions', 'childs_chair', 'special_requests']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']