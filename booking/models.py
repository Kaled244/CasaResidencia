from django.db import models
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Hotel(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='hotels/')
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name

User = settings.AUTH_USER_MODEL

class PromoCode(models.Model):
    code = models.CharField(max_length=12, unique=True)  # uppercase alnum
    discount_percent = models.PositiveSmallIntegerField()  # e.g., 30 for 30%
    expiry_date = models.DateField()
    usage_limit = models.PositiveIntegerField(default=0)  # 0 = unlimited
    one_time_per_account = models.BooleanField(default=True)
    used_by = models.ManyToManyField(User, blank=True, related_name='used_promos')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"

    def is_valid_now(self):
        return timezone.localdate() <= self.expiry_date

    def usage_count(self):
        return self.used_by.count()

    def remaining_uses(self):
        if self.usage_limit == 0:
            return None
        return max(0, self.usage_limit - self.usage_count())


class Booking(models.Model):
    PAYMENT_CHOICES = [
        ('card', 'Credit Card'),
        ('gcash', 'GCash'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    hotel = models.ForeignKey('Hotel', on_delete=models.PROTECT)  # assumes you have Hotel model
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxes_and_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    transaction_ref = models.CharField(max_length=64, unique=True, db_index=True)
    promo = models.ForeignKey(PromoCode, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_ref} - {self.hotel} - {self.total}"
