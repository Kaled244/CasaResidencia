from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from .models import Room, Booking, Category
from .forms import SearchForm, BookingForm
from django.utils import timezone


def home(request):
    form = SearchForm(request.GET or None)
    return render(request, 'bookings/home.html', {'form': form})


def room_list(request):
    # Get search criteria
    location = request.GET.get('location', '')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    guests = request.GET.get('guests')

    # Filters
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_rating = request.GET.get('min_rating')

    rooms = Room.objects.all()

    # Validate basic inputs
    error = None
    if not (location and check_in and check_out and guests):
        error = "Please input the missing fields"
    else:
        try:
            check_in_date = timezone.datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = timezone.datetime.strptime(check_out, '%Y-%m-%d').date()
            if check_in_date < timezone.localdate() or check_out_date <= check_in_date:
                error = "Please select valid check-in and check-out dates."
        except Exception:
            error = "Please select valid check-in and check-out dates."
        try:
            guests = int(guests)
            if guests < 1:
                error = "Please enter a valid number of guests."
        except Exception:
            error = "Please enter a valid number of guests."

    if error:
        messages.error(request, error)
        # Render home with errors
        form = SearchForm(request.GET or None)
        return render(request, 'bookings/home.html', {'form': form})

    # Now filter available rooms
    available = Room.objects.available(check_in_date, check_out_date, location)

    if category_id:
        available = available.filter(category_id=category_id)
    if min_price:
        try:
            available = available.filter(price_per_night__gte=min_price)
        except Exception:
            pass
    if max_price:
        try:
            available = available.filter(price_per_night__lte=max_price)
        except Exception:
            pass
    if min_rating:
        try:
            available = available.filter(rating__gte=min_rating)
        except Exception:
            pass

    if not available.exists():
        messages.info(request, 'No rooms available with the selected filters.')

    categories = Category.objects.all()

    context = {
        'rooms': available,
        'check_in': check_in,
        'check_out': check_out,
        'guests': guests,
        'location': location,
        'categories': categories,
    }
    return render(request, 'bookings/room_list.html', context)


def book_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    # Expect check_in/check_out/guests via GET or POST
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            try:
                booking.full_clean()
            except Exception as e:
                messages.error(request, e.message)
                return redirect(request.META.get('HTTP_REFERER', reverse('bookings:room_list')))
            booking.save()
            messages.success(request, 'Booking confirmed successfully!')
            return redirect(booking.get_absolute_url())
    else:
        # Pre-populate a form if query params provided
        initial = {
            'check_in': request.GET.get('check_in'),
            'check_out': request.GET.get('check_out'),
            'guests': request.GET.get('guests'),
        }
        form = BookingForm(initial=initial)
        form.fields['room'].queryset = Room.objects.filter(pk=room.pk)
    return render(request, 'bookings/book_room.html', {'form': form, 'room': room})


def booking_confirm(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, 'bookings/booking_confirm.html', {'booking': booking})
