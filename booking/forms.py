from django import forms
from django.core.exceptions import ValidationError
import re
from .models import PromoCode
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('A user with that email already exists.')
        return email

ALNUM_UPPER_RE = re.compile(r'^[A-Z0-9]{6,12}$')

class PromoApplyForm(forms.Form):
    promo_code = forms.CharField(max_length=12, required=False)

    def clean_promo_code(self):
        code = self.cleaned_data.get('promo_code', '').strip().upper()
        if not code:
            return ''
        if not ALNUM_UPPER_RE.match(code):
            raise ValidationError('Promo codes must be uppercase alphanumeric (6-12 chars).')
        try:
            promo = PromoCode.objects.get(code=code)
        except PromoCode.DoesNotExist:
            raise ValidationError('Invalid promo code.')
        if not promo.is_valid_now():
            raise ValidationError('Promo code expired.')
        # usage limit check (if limit > 0)
        if promo.usage_limit and promo.usage_count() >= promo.usage_limit:
            raise ValidationError('Promo code usage limit reached.')
        # pass PromoCode object for convenience
        self.cleaned_data['promo_obj'] = promo
        return code


class CheckoutForm(forms.Form):
    check_in = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    check_out = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    guests = forms.IntegerField(min_value=1, initial=1)
    payment_method = forms.ChoiceField(choices=[('card','Credit Card'), ('gcash','GCash')])
    # Credit card fields (optional if payment_method card)
    card_number = forms.CharField(required=False, max_length=19)
    card_expiry = forms.CharField(required=False)  # MM/YY
    card_cvv = forms.CharField(required=False, max_length=4)
    # GCash
    gcash_number = forms.CharField(required=False)

    promo_code = forms.CharField(required=False)

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get('payment_method')
        if method == 'card':
            number = cleaned.get('card_number','').replace(' ','')
            if not number or not number.isdigit() or len(number) not in (15,16):
                raise ValidationError("Invalid card number.")
            # expiry and cvv simple checks:
            if not cleaned.get('card_expiry'):
                raise ValidationError("Card expiry required.")
            if not cleaned.get('card_cvv') or not cleaned.get('card_cvv').isdigit():
                raise ValidationError("Invalid CVV.")
        elif method == 'gcash':
            num = cleaned.get('gcash_number','').strip()
            if not num or not num.isdigit() or len(num) < 10:
                raise ValidationError("Invalid GCash number.")
        return cleaned
