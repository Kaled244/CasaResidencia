from django.urls import path
from . import views

urlpatterns = [
    path('hotel/<int:hotel_id>/checkout/', views.checkout, name='checkout'),
    path('booking/confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
]
