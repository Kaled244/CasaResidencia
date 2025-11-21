from django import forms
from .models import Booking, Room, Category


class SearchForm(forms.Form):
    location = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'placeholder': 'City or location'}))
    check_in = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    check_out = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    guests = forms.IntegerField(min_value=1)


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'check_in', 'check_out', 'guests']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        # Model clean will validate more, so allow it to raise if needed
        return cleaned
