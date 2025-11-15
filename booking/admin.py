from django.contrib import admin
from .models import Hotel

from django.contrib import admin
from .models import Booking, PromoCode

admin.site.register(Hotel)

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code','discount_percent','expiry_date','usage_limit','one_time_per_account')
    search_fields = ('code',)
    list_filter = ('expiry_date','one_time_per_account')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('transaction_ref','hotel','user','total','payment_method','status','created_at')
    search_fields = ('transaction_ref','user__username','hotel__name')
    list_filter = ('status','payment_method','created_at')
