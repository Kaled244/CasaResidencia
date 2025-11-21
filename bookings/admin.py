from django.contrib import admin
from .models import Category, Room, Booking


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'location', 'price_per_night', 'rating')
    list_filter = ('category', 'location')
    search_fields = ('name', 'location')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('reference', 'room', 'check_in', 'check_out', 'guests', 'total_price')
    list_filter = ('check_in', 'check_out', 'room')
    readonly_fields = ('reference', 'total_price', 'created_at')
