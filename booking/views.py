from django.shortcuts import render, get_object_or_404
from .models import Hotel
from django.db.models import Q


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Booking, PromoCode
from .forms import CheckoutForm, PromoApplyForm
from .utils import generate_transaction_ref
from decimal import Decimal
import random
from django.urls import reverse

def booking_form(request):
    return render(request, 'booking/booking_form.html')

# def home(request):
#     hotels = Hotel.objects.all()
#     return render(request, 'registration/home.html', {'hotels': hotels})

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    return render(request, 'booking/hotel_detail.html', {'hotel': hotel})

def index(request):
    return render(request, 'registration/index.html')  # landing page

def home(request):
    query = request.GET.get('q', '')

    if query:
        hotels = Hotel.objects.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )
    else:
        hotels = Hotel.objects.all()

    return render(request, 'registration/home.html', {
        'hotels': hotels
    })

def checkout(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    nights = 1
    subtotal = Decimal(hotel.price_per_night or 0)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        promo_form = PromoApplyForm(request.POST)

        if form.is_valid():
            cleaned = form.cleaned_data
            # calculate nights
            check_in = cleaned['check_in']
            check_out = cleaned['check_out']
            nights = max(1, (check_out - check_in).days)
            subtotal = Decimal(hotel.price_per_night) * nights

            # handle promo code
            promo_obj = None
            discount_amount = Decimal('0.00')
            promo_code_value = cleaned.get('promo_code', '').strip()
            if promo_code_value:
                try:
                    promo = PromoCode.objects.get(code__iexact=promo_code_value)
                except PromoCode.DoesNotExist:
                    messages.error(request, "Invalid promo code.")
                    return redirect(request.path)

                # validate promo
                if not promo.is_valid_now():
                    messages.error(request, "Promo code expired.")
                    return redirect(request.path)
                if promo.usage_limit and promo.usage_count() >= promo.usage_limit:
                    messages.error(request, "Promo code usage limit reached.")
                    return redirect(request.path)
                if promo.one_time_per_account and request.user.is_authenticated and promo.used_by.filter(pk=request.user.pk).exists():
                    messages.error(request, "This promo code has already been used with your account.")
                    return redirect(request.path)

                promo_obj = promo
                discount_amount = (subtotal * Decimal(promo.discount_percent) / Decimal(100)).quantize(Decimal('0.01'))

            # calculate taxes and total
            taxes = (subtotal - discount_amount) * Decimal('0.12')  # 12% VAT example
            total = (subtotal - discount_amount + taxes).quantize(Decimal('0.01'))

            # simulate payment
            payment_method = cleaned['payment_method']
            payment_success = simulate_payment(payment_method)

            # create booking inside transaction
            with transaction.atomic():
                tx_ref = generate_transaction_ref()
                booking = Booking.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    hotel=hotel,
                    check_in=check_in,
                    check_out=check_out,
                    guests=cleaned['guests'],
                    subtotal=subtotal,
                    discount_amount=discount_amount,
                    taxes_and_fees=taxes,
                    total=total,
                    payment_method=payment_method,
                    transaction_ref=tx_ref,
                    promo=promo_obj,
                    status='paid' if payment_success else 'failed'
                )

                # record promo usage if success and promo set
                if payment_success and promo_obj and request.user.is_authenticated:
                    promo_obj.used_by.add(request.user)

            if payment_success:
                messages.success(request, f"Payment successful! Transaction ref: {tx_ref}")
                return redirect(reverse('booking_confirmation', args=[booking.id]))
            else:
                messages.error(request, "Payment failed. Please try again.")
                return redirect(request.path)

        else:
            # form invalid
            messages.error(request, "Please fix the errors in the form.")
            return redirect(request.path)

    else:
        form = CheckoutForm(initial={'payment_method': 'card'})
        promo_form = PromoApplyForm()

    context = {
        'hotel': hotel,
        'form': form,
        'promo_form': promo_form,
        'subtotal': subtotal,
        'nights': nights,
    }
    return render(request, 'booking/checkout.html', context)



def simulate_payment(method):
    """
    Simulation only: deterministic-ish but sometimes fail for demonstration.
    - card: 95% success
    - gcash: 90% success with occasional timeout simulated
    """
    if method == 'card':
        return random.random() < 0.95
    if method == 'gcash':
        # simulate occasional timeout/failure
        return random.random() < 0.90
    return False


def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking/booking_confirmation.html', {'booking': booking})
