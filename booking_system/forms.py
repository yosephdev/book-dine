from django import forms
from .models import Reservation, Review, Table


class ReservationForm(forms.ModelForm):
    table = forms.ModelChoiceField(queryset=Table.objects.filter(status='available'))

    class Meta:
        model = Reservation
        fields = ['table', 'number_of_guests', 'date', 'time', 'dietary_restrictions', 'childs_chair', 'special_requests']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['table'].queryset = Table.objects.filter(status='available')
   

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']