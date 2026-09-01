from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
	FlightBookingViewSet,
	HotelBookingViewSet,
	PackageBookingViewSet,
    PlanBookingViewSet,
)

router = SimpleRouter()
router.register('flights', FlightBookingViewSet, basename='flight-booking')
router.register('hotels', HotelBookingViewSet, basename='hotel-booking')
router.register('packages', PackageBookingViewSet, basename='package-booking')
router.register('plans', PlanBookingViewSet, basename='plan-booking')

urlpatterns = [
	path('', include(router.urls)),
]
