from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.room_list, name='room_list'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('confirmed/<int:pk>/', views.booking_confirm, name='booking_confirm'),
]
