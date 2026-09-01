from django.db.models import Q
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.decorators import user_required
from .models import Flight
from bookings.models import FlightBooking
import requests



# ======================================
# API / Website Flight List
# ======================================

def flight_list(request):

    q = request.GET.get('q', '').strip()
    flights = Flight.objects.all()

    if q:
        flights = flights.filter(
            Q(origin__icontains=q) |
            Q(destination__icontains=q) |
            Q(airline__name__icontains=q)
        )

    return render(
        request,
        "flights/list.html",
        {
            "flights": flights,
            "search_query": q,
        }
    )



# Keep this name also for your MyTrip urls.py
def flight_list_template(request):

    return flight_list(request)



# ======================================
# Flight Details + Weather API
# ======================================

def flight_detail_template(request, pk):

    flight = get_object_or_404(
        Flight,
        pk=pk
    )


    weather = None


    q = None
    if flight.place and flight.place.city:
        q = flight.place.city
    elif flight.destination:
        q = flight.destination

    if q:
        api_key = getattr(settings, 'WEATHER_API_KEY', None)
        url = "https://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": q
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                weather = response.json()
        except requests.exceptions.RequestException:
            weather = None



    return render(
        request,

        "flights/detail.html",

        {
            "flight": flight,

            "weather": weather
        }
    )



# ======================================
# Booking Page
# ======================================

@user_required
def flight_book_view(request, pk):
    flight = get_object_or_404(Flight, pk=pk)

    if request.method == 'POST':
        passenger_name = (request.POST.get('name') or '').strip()
        if not passenger_name:
            messages.error(request, 'Passenger name is required.')
            return render(request, 'flights/book.html', {'flight': flight})

        booking = FlightBooking.objects.create(
            user=request.user,
            flight=flight,
            total_price=flight.price,
            booking_status='pending',
        )
        messages.success(request, f'Flight booking created successfully. Your booking ID is #{booking.id}. Use Pay Now to complete payment.')
        return redirect('bookings_page')

    return render(request, 'flights/book.html', {'flight': flight})