from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView
from MyTrip import views
from packages import views as packages_views
from accounts import views as accounts_views
from flights import views as flights_views
from hotels import views as hotels_views

urlpatterns = [
    path('', views.index, name='MyTrip'),
    path('flights/', flights_views.flight_list_template, name='flights_page'),
    path('flights/<int:pk>/', flights_views.flight_detail_template, name='flight_detail'),
    path('flights/<int:pk>/book/', flights_views.flight_book_view, name='flight_book'),
    path('flights/', flights_views.flight_list_template, name='flights_page'),
    path('hotels/', hotels_views.hotel_list_template, name='hotels_page'),
    path('hotels/<int:pk>/', hotels_views.hotel_detail_template, name='hotel_detail'),
    path('hotels/<int:pk>/book/', hotels_views.hotel_book_view, name='hotel_book'),
    path('packages/', packages_views.package_list_view, name='packages_page'),
    path('packages/<int:pk>/', packages_views.package_detail_view, name='package_detail'),
    path('packages/<int:pk>/book/', packages_views.package_book_view, name='package_book'),
    path('bookings/', views.bookings_page, name='bookings_page'),
    path('bookings/statuses/', views.booking_statuses, name='booking_statuses'),
    path('bookings/flight/<int:pk>/', views.flight_booking_detail, name='flight_booking_detail'),
    path('bookings/hotel/<int:pk>/', views.hotel_booking_detail, name='hotel_booking_detail'),
    path('bookings/package/<int:pk>/', views.package_booking_detail, name='package_booking_detail'),
    path('bookings/flight/<int:pk>/cancel/', views.flight_booking_cancel, name='flight_booking_cancel'),
    path('bookings/hotel/<int:pk>/cancel/', views.hotel_booking_cancel, name='hotel_booking_cancel'),
    path('bookings/package/<int:pk>/cancel/', views.package_booking_cancel, name='package_booking_cancel'),
    
    path('payments/', views.payments_page, name='payments_page'),
    path('checkout/<str:booking_type>/<int:pk>/', views.checkout, name='checkout'),
    path('dashboard/', views.dashboard_page, name='dashboard_page'),
    path('dashboard/details/<str:stat>/', views.dashboard_detail, name='dashboard_detail'),
    path('reviews/', views.reviews_page, name='reviews_page'),
    path('search/', views.search, name='search'),
    path('offers/', views.offers_page, name='offers_page'),

    # Authentication (template-based)
    path('accounts/register/', accounts_views.register_view, name='register'),
    path('accounts/login/', accounts_views.login_view, name='login'),
    path('accounts/logout/', accounts_views.logout_view, name='logout'),
    
    path('subscribe/', views.subscribe, name='subscribe'),

    # Dashboards
    path('user/dashboard/', accounts_views.user_dashboard, name='user_dashboard'),
    # The project previously exposed a custom admin dashboard at '/dashboard/admin/'.
    # Redirect legacy/custom admin dashboard URLs to the standard Django admin site.
    path('dashboard/admin/', RedirectView.as_view(url='/admin/', permanent=False)),
    # Backwards-compatible redirect from old admin path
    path('admin/dashboard/', RedirectView.as_view(url='/admin/', permanent=False)),
]