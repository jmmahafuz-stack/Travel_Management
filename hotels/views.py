from django.db.models import Q
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Hotel
from accounts.decorators import user_required
from django.contrib import messages
from bookings.models import HotelBooking
import requests



def hotel_list_template(request):

    q = request.GET.get('q', '').strip()
    hotels = Hotel.objects.all().order_by('name')

    if q:
        hotels = hotels.filter(
            Q(name__icontains=q) | Q(city__icontains=q)
        )

    return render(
        request,
        "hotels/list.html",
        {
            "hotels": hotels,
            "search_query": q,
        }
    )



def hotel_detail_template(request, pk):

    hotel = get_object_or_404(
        Hotel,
        pk=pk
    )


    weather = None


    q = None
    if hotel.place and hotel.place.city:
        q = hotel.place.city
    elif hotel.city:
        q = hotel.city

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
        "hotels/detail.html",
        {
            "hotel": hotel,
            "weather": weather
        }
    )




@user_required
def hotel_book_view(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)

    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        if not check_in or not check_out:
            messages.error(request, 'Check-in and check-out dates are required.')
            return render(request, 'hotels/book.html', {'hotel': hotel})

        try:
            check_in_date = timezone.datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = timezone.datetime.strptime(check_out, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Please enter valid dates.')
            return render(request, 'hotels/book.html', {'hotel': hotel})

        if check_out_date <= check_in_date:
            messages.error(request, 'Check-out date must be after check-in date.')
            return render(request, 'hotels/book.html', {'hotel': hotel})

        nights = (check_out_date - check_in_date).days
        total_price = hotel.price_per_night * nights

        booking = HotelBooking.objects.create(
            user=request.user,
            hotel=hotel,
            check_in=check_in_date,
            check_out=check_out_date,
            total_price=total_price,
            booking_status='pending',
        )
        messages.success(request, f'Hotel booking created successfully. Your booking ID is #{booking.id}. Use Pay Now to complete payment.')
        return redirect('bookings_page')

    return render(request, 'hotels/book.html', {'hotel': hotel})