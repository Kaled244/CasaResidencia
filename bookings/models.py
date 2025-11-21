import uuid
from decimal import Decimal
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class RoomQuerySet(models.QuerySet):
    def available(self, check_in, check_out, location=None):
        if not check_in or not check_out:
            return self
        qs = self
        if location:
            qs = qs.filter(location__icontains=location)
        # Exclude rooms that have bookings that overlap
        overlapping = Booking.objects.filter(
            room=models.OuterRef('pk'),
            check_in__lt=check_out,
            check_out__gt=check_in,
        )
        return qs.annotate(has_overlap=models.Exists(overlapping)).filter(has_overlap=False)


class Room(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    location = models.CharField(max_length=200, default='')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    description = models.TextField(blank=True)

    objects = RoomQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} — {self.location}"


def generate_reference():
    return uuid.uuid4().hex[:10].upper()


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=20, unique=True, default=generate_reference)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        today = timezone.localdate()
        if self.check_in < today or self.check_out < today:
            raise ValidationError("Please select valid check-in and check-out dates.")
        if self.check_out <= self.check_in:
            raise ValidationError("Please select valid check-in and check-out dates.")
        if self.guests < 1:
            raise ValidationError("Please enter a valid number of guests.")
        # Check overlapping bookings
        overlaps = Booking.objects.filter(
            room=self.room,
            check_in__lt=self.check_out,
            check_out__gt=self.check_in,
        )
        if self.pk:
            overlaps = overlaps.exclude(pk=self.pk)
        if overlaps.exists():
            raise ValidationError("Room not available for the selected dates.")

    def save(self, *args, **kwargs):
        nights = (self.check_out - self.check_in).days
        self.total_price = (self.room.price_per_night or Decimal('0.00')) * Decimal(nights)
        if not self.reference:
            self.reference = generate_reference()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('bookings:booking_confirm', args=[self.pk])

    def __str__(self):
        return f"Booking {self.reference} — {self.room}"
