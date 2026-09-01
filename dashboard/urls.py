"""
URLs for the dashboard app.

Provides a minimal endpoint so app URLs can be included safely.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.packages_list, name='dashboard-home'),
    path('admin-home/', views.admin_home, name='admin-home'),
    path('health/', views.health_check, name='dashboard-health'),

    # Management UI for Flights
    path('manage/flights/', views.flights_list, name='dashboard-manage-flights'),
    path('manage/flights/add/', views.flight_create, name='dashboard-manage-flights-add'),
    path('manage/flights/<int:pk>/edit/', views.flight_edit, name='dashboard-manage-flights-edit'),
    path('manage/flights/<int:pk>/delete/', views.flight_delete, name='dashboard-manage-flights-delete'),

    # Management UI for Hotels
    path('manage/hotels/', views.hotels_list, name='dashboard-manage-hotels'),
    path('manage/hotels/add/', views.hotel_create, name='dashboard-manage-hotels-add'),
    path('manage/hotels/<int:pk>/edit/', views.hotel_edit, name='dashboard-manage-hotels-edit'),
    path('manage/hotels/<int:pk>/delete/', views.hotel_delete, name='dashboard-manage-hotels-delete'),

    # Management UI for Packages
    path('manage/packages/', views.packages_list, name='dashboard-manage-packages'),
    path('manage/packages/add/', views.package_create, name='dashboard-manage-packages-add'),
    path('manage/packages/<int:pk>/edit/', views.package_edit, name='dashboard-manage-packages-edit'),
    path('manage/packages/<int:pk>/delete/', views.package_delete, name='dashboard-manage-packages-delete'),
    # Bookings management
    path('manage/bookings/', views.bookings_list, name='dashboard-manage-bookings'),
    path('manage/bookings/<str:btype>/<int:pk>/<str:action>/', views.booking_action, name='dashboard-manage-booking-action'),
    path('manage/profile/', views.profile_edit, name='dashboard-profile-edit'),
]
