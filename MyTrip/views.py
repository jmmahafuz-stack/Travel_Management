"""
Front-end views for the small MyTrip site pages.

These views provide simple placeholder pages (Flights, Hotels, Packages, etc.)
and a lightweight `search` view that queries the existing models. They are
implemented as minimal, safe pages that do not alter API behavior. The
search function performs small, read-only queries and is intentionally
conservative in what it searches to avoid heavy database loads.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from accounts.decorators import user_required
from django.db.models import Q, Sum


def index(request):
    """Home page for the website."""
    # Provide some sample items for homepage cards (best-effort)
    try:
        from flights.models import Flight
        from hotels.models import Hotel
        from packages.models import Package

        flights = Flight.objects.select_related('airline').all().order_by('-created_at')[:3]
        hotels = Hotel.objects.all().order_by('-id')[:3]
        packages = Package.objects.all().order_by('-id')[:3]

        # Prefer an admin-provided site option for hero (background & texts)
        hero_image = None
        hero_heading = None
        hero_subheading = None
        search_placeholder = None
        try:
            from core.models import SiteOption
            opt = SiteOption.objects.first()
            if opt:
                if getattr(opt, 'hero_image', None):
                    try:
                        hero_image = opt.hero_image.url
                    except Exception:
                        hero_image = None
                hero_heading = opt.hero_heading
                hero_subheading = opt.hero_subheading
                search_placeholder = opt.search_placeholder
        except Exception:
            pass

    except Exception:
        flights = []
        hotels = []
        packages = []

    # Build context and fall back to static hero if needed
    ctx = {'flights': flights, 'hotels': hotels, 'packages': packages}
    if hero_image:
        ctx['hero_image'] = hero_image
    if hero_heading:
        ctx['hero_heading'] = hero_heading
    if hero_subheading:
        ctx['hero_subheading'] = hero_subheading
    if search_placeholder:
        ctx['search_placeholder'] = search_placeholder

    return render(request, 'MyTrip/index.html', ctx)


def flights_page(request):
    """Simple flights page placeholder."""
    # Try to find a flight with a hero image to use as the page hero
    hero = None
    try:
        from flights.models import Flight
        flight = Flight.objects.filter(hero_image__isnull=False).exclude(hero_image='').first()
        if flight and getattr(flight, 'hero_image', None):
            hero = flight.hero_image.url
    except Exception:
        hero = None

    return render(request, 'MyTrip/flights.html', {'hero_image': hero})


def hotels_page(request):
    """Simple hotels page placeholder."""
    hero = None
    try:
        from hotels.models import Hotel
        hotel = Hotel.objects.filter(hero_image__isnull=False).exclude(hero_image='').first()
        if hotel and getattr(hotel, 'hero_image', None):
            hero = hotel.hero_image.url
    except Exception:
        hero = None

    return render(request, 'MyTrip/hotels.html', {'hero_image': hero})


def packages_page(request):
    """Simple packages page placeholder."""
    hero = None
    try:
        from packages.models import Package
        pkg = Package.objects.filter(hero_image__isnull=False).exclude(hero_image='').first()
        if pkg and getattr(pkg, 'hero_image', None):
            hero = pkg.hero_image.url
    except Exception:
        hero = None

    return render(request, 'MyTrip/packages.html', {'hero_image': hero})


@user_required
def bookings_page(request):
    """List the current user's bookings (flight, hotel, package)."""
    from bookings.models import FlightBooking, HotelBooking, PackageBooking
    from payments.models import Payment

    flights = FlightBooking.objects.filter(user=request.user)
    hotels = HotelBooking.objects.filter(user=request.user)
    packages = PackageBooking.objects.filter(user=request.user)

    # Build a unified list of bookings for card UI
    all_bookings = []
    for b in flights:
        paid = Payment.objects.filter(booking_type='flight', booking_id=b.id, payment_status='paid').exists()
        # include a few detail fields for the quick right-side view panel
        try:
            airline_name = b.flight.airline.name
        except Exception:
            airline_name = ''
        departure = ''
        arrival = ''
        seat_class = ''
        try:
            if getattr(b.flight, 'departure_time', None):
                departure = b.flight.departure_time.strftime("%Y-%m-%d %H:%M")
            if getattr(b.flight, 'arrival_time', None):
                arrival = b.flight.arrival_time.strftime("%Y-%m-%d %H:%M")
            if hasattr(b.flight, 'get_seat_class_display'):
                seat_class = b.flight.get_seat_class_display()
        except Exception:
            pass

        all_bookings.append({
            'type': 'flight',
            'pk': b.pk,
            'title': f"{airline_name} — {b.flight.origin} → {b.flight.destination}",
            'subtitle': departure,
            'price': b.total_price,
            'status': b.booking_status,
            'created_at': b.created_at,
            'paid': paid,
            'airline': airline_name,
            'origin': b.flight.origin,
            'destination': b.flight.destination,
            'departure_time': departure,
            'arrival_time': arrival,
            'seat_class': seat_class,
            'detail_url': f"/bookings/flight/{b.pk}/",
        })
    for b in hotels:
        paid = Payment.objects.filter(booking_type='hotel', booking_id=b.id, payment_status='paid').exists()
        check_in = str(b.check_in) if getattr(b, 'check_in', None) else ''
        check_out = str(b.check_out) if getattr(b, 'check_out', None) else ''
        all_bookings.append({
            'type': 'hotel',
            'pk': b.pk,
            'title': b.hotel.name,
            'subtitle': f"{b.hotel.city} • {check_in} → {check_out}",
            'price': b.total_price,
            'status': b.booking_status,
            'created_at': b.created_at,
            'paid': paid,
            'hotel_name': b.hotel.name,
            'hotel_city': b.hotel.city,
            'check_in': check_in,
            'check_out': check_out,
            'detail_url': f"/bookings/hotel/{b.pk}/",
        })
    for b in packages:
        paid = Payment.objects.filter(booking_type='package', booking_id=b.id, payment_status='paid').exists()
        pkg = getattr(b, 'package', None)
        pkg_title = pkg.title if pkg else ''
        pkg_dest = pkg.destination if pkg else ''
        pkg_duration = getattr(pkg, 'duration_days', '') if pkg else ''
        pkg_desc = getattr(pkg, 'description', '') if pkg else ''
        all_bookings.append({
            'type': 'package',
            'pk': b.pk,
            'title': pkg_title,
            'subtitle': pkg_dest,
            'price': b.total_price,
            'status': b.booking_status,
            'created_at': b.created_at,
            'paid': paid,
            'package_title': pkg_title,
            'package_destination': pkg_dest,
            'package_duration': pkg_duration,
            'package_description': pkg_desc,
            'detail_url': f"/bookings/package/{b.pk}/",
        })
    # sort newest first
    all_bookings.sort(key=lambda x: x['created_at'], reverse=True)

    return render(request, 'MyTrip/bookings.html', {'all_bookings': all_bookings})


@user_required
def flight_booking_detail(request, pk):
    from bookings.models import FlightBooking
    booking = get_object_or_404(FlightBooking, pk=pk, user=request.user)
    from payments.models import Payment
    is_paid = Payment.objects.filter(booking_type='flight', booking_id=booking.id, payment_status='paid').exists()
    return render(request, 'MyTrip/flight_booking_detail.html', {'booking': booking, 'is_paid': is_paid})


@user_required
def hotel_booking_detail(request, pk):
    from bookings.models import HotelBooking
    booking = get_object_or_404(HotelBooking, pk=pk, user=request.user)
    from payments.models import Payment
    is_paid = Payment.objects.filter(booking_type='hotel', booking_id=booking.id, payment_status='paid').exists()
    # Compute nights safely (difference in days between check_out and check_in)
    nights = ''
    try:
        if getattr(booking, 'check_in', None) and getattr(booking, 'check_out', None):
            delta = booking.check_out - booking.check_in
            nights = delta.days if hasattr(delta, 'days') else ''
    except Exception:
        nights = ''

    return render(request, 'MyTrip/hotel_booking_detail.html', {'booking': booking, 'is_paid': is_paid, 'nights': nights})


@user_required
def package_booking_detail(request, pk):
    from bookings.models import PackageBooking
    booking = get_object_or_404(PackageBooking, pk=pk, user=request.user)
    from payments.models import Payment
    is_paid = Payment.objects.filter(booking_type='package', booking_id=booking.id, payment_status='paid').exists()
    return render(request, 'MyTrip/package_booking_detail.html', {'booking': booking, 'is_paid': is_paid})



@user_required
def checkout(request, booking_type, pk):
    """Display a simple checkout page for a booking; form posts to payments checkout handler."""
    from payments.models import Payment
    from bookings.models import FlightBooking, HotelBooking, PackageBooking, PlanBooking

    booking = None
    if booking_type == 'flight':
        booking = get_object_or_404(FlightBooking, pk=pk, user=request.user)
    elif booking_type == 'hotel':
        booking = get_object_or_404(HotelBooking, pk=pk, user=request.user)
    elif booking_type == 'package':
        booking = get_object_or_404(PackageBooking, pk=pk, user=request.user)
    
    else:
        messages.error(request, 'Invalid booking type')
        return redirect('bookings_page')

    is_paid = Payment.objects.filter(booking_type=booking_type, booking_id=booking.id, payment_status='paid').exists()
    # Provide admin-configurable payment/account info to the checkout template.
    # Support both `account_number` (preferred) and legacy `bkash_number` field.
    account_number = ''
    bkash_number = ''
    try:
        from payments.models import PaymentOption
        opt = PaymentOption.objects.first()
        if opt:
            bkash_number = getattr(opt, 'bkash_number', '') or ''
            account_number = getattr(opt, 'account_number', '') or bkash_number
    except Exception:
        account_number = ''
        bkash_number = ''

    return render(request, 'MyTrip/checkout.html', {
        'booking': booking,
        'booking_type': booking_type,
        'is_paid': is_paid,
        'account_number': account_number,
        'bkash_number': bkash_number,
    })


@user_required
def booking_statuses(request):
    """Return JSON with booking status and paid flag for the current user.

    Response format: {"bookings": [{"type":"flight","id":123,"status":"pending","paid":false}, ...]}
    """
    from bookings.models import FlightBooking, HotelBooking, PackageBooking
    from payments.models import Payment

    out = []
    models = (
        ('flight', FlightBooking),
        ('hotel', HotelBooking),
        ('package', PackageBooking),
    )
    for btype, model in models:
        qs = model.objects.filter(user=request.user).values('id', 'booking_status')
        for row in qs:
            paid = Payment.objects.filter(booking_type=btype, booking_id=row['id'], payment_status='paid').exists()
            out.append({'type': btype, 'id': row['id'], 'status': row['booking_status'], 'paid': paid})

    return JsonResponse({'bookings': out})


@user_required
def flight_booking_cancel(request, pk):
    from bookings.models import FlightBooking
    booking = get_object_or_404(FlightBooking, pk=pk, user=request.user)
    if request.method == 'POST':
        if booking.booking_status != 'cancelled':
            booking.booking_status = 'cancelled'
            booking.save()
            messages.success(request, 'Flight booking cancelled.')
        else:
            messages.info(request, 'Booking is already cancelled.')
    return redirect('bookings_page')


@user_required
def hotel_booking_cancel(request, pk):
    from bookings.models import HotelBooking
    booking = get_object_or_404(HotelBooking, pk=pk, user=request.user)
    if request.method == 'POST':
        if booking.booking_status != 'cancelled':
            booking.booking_status = 'cancelled'
            booking.save()
            messages.success(request, 'Hotel booking cancelled.')
        else:
            messages.info(request, 'Booking is already cancelled.')
    return redirect('bookings_page')


@user_required
def package_booking_cancel(request, pk):
    from bookings.models import PackageBooking
    booking = get_object_or_404(PackageBooking, pk=pk, user=request.user)
    if request.method == 'POST':
        if booking.booking_status != 'cancelled':
            booking.booking_status = 'cancelled'
            booking.save()
            messages.success(request, 'Package booking cancelled.')
        else:
            messages.info(request, 'Booking is already cancelled.')
    return redirect('bookings_page')


@user_required
def plan_booking_cancel(request, pk):
    from bookings.models import PlanBooking
    booking = get_object_or_404(PlanBooking, pk=pk, user=request.user)
    if request.method == 'POST':
        if booking.booking_status != 'cancelled':
            booking.booking_status = 'cancelled'
            booking.save()
            messages.success(request, 'Plan booking cancelled.')
        else:
            messages.info(request, 'Booking is already cancelled.')
    return redirect('bookings_page')


def payments_page(request):
    """Simple payments page placeholder."""

    return render(request, 'MyTrip/payments.html')


def dashboard_page(request):
    """Dashboard with quick stats: total users, total bookings, revenue."""
    from accounts.models import User
    from bookings.models import FlightBooking, HotelBooking, PackageBooking
    from payments.models import Payment

    total_users = User.objects.count()
    total_bookings = (
        FlightBooking.objects.count()
        + HotelBooking.objects.count()
        + PackageBooking.objects.count()
    )
    revenue = Payment.objects.filter(payment_status='paid').aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'MyTrip/dashboard.html', {'total_users': total_users, 'total_bookings': total_bookings, 'revenue': revenue})


@staff_member_required
def dashboard_detail(request, stat):
    """Show detail lists for dashboard stats: users, bookings, revenue."""
    from accounts.models import User
    from bookings.models import FlightBooking, HotelBooking, PackageBooking
    from payments.models import Payment

    context = {'stat': stat}
    if stat == 'users':
        context['items'] = User.objects.all().order_by('-date_joined')[:200]
    elif stat == 'bookings':
        # Show recent bookings grouped by type
        flights = FlightBooking.objects.select_related('flight', 'user').order_by('-created_at')[:100]
        hotels = HotelBooking.objects.select_related('hotel', 'user').order_by('-created_at')[:100]
        packages = PackageBooking.objects.select_related('package', 'user').order_by('-created_at')[:100]
        context['flights'] = flights
        context['hotels'] = hotels
        context['packages'] = packages
    elif stat == 'revenue':
        context['payments'] = Payment.objects.order_by('-created_at')[:200]
    else:
        messages.error(request, 'Unknown stat')
        return redirect('dashboard_page')

    return render(request, 'MyTrip/dashboard_details.html', context)


def reviews_page(request):
    """Simple reviews placeholder page."""

    return render(request, 'MyTrip/reviews.html')


def offers_page(request):
    """Simple offers page that highlights package deals (placeholder)."""

    # Prefer packages explicitly marked as offers, fall back to price threshold
    from packages.models import Package
    offers = Package.objects.filter(Q(is_offer=True) | Q(price__lte=200))[:20]
    return render(request, 'MyTrip/offers.html', {'offers': offers})


def search(request):
    """Lightweight search across models.

    - Reads `q` (query) and `type` (category) from GET parameters.
    - Performs small, case-insensitive lookups on common text fields.
    - Results are returned in a dictionary keyed by model name.
    """

    q = request.GET.get('q', '').strip()
    category = request.GET.get('type', 'all')
    results = {}

    if q:
        # Flights
        if category in ('all', 'flights'):
            try:
                from flights.models import Flight

                results['flights'] = list(
                    Flight.objects.filter(
                        Q(origin__icontains=q) | Q(destination__icontains=q) | Q(airline__name__icontains=q)
                    ).values('id', 'airline_id', 'origin', 'destination', 'price')[:20]
                )
            except Exception:
                results['flights'] = []

        # Hotels
        if category in ('all', 'hotels'):
            try:
                from hotels.models import Hotel

                results['hotels'] = list(
                    Hotel.objects.filter(Q(name__icontains=q) | Q(city__icontains=q)).values('id', 'name', 'city', 'price_per_night')[:20]
                )
            except Exception:
                results['hotels'] = []

        # Packages
        if category in ('all', 'packages'):
            try:
                from packages.models import Package

                results['packages'] = list(
                    Package.objects.filter(Q(title__icontains=q) | Q(destination__icontains=q)).values('id', 'title', 'destination', 'price')[:20]
                )
            except Exception:
                results['packages'] = []

        # Places
        if category in ('all', 'places'):
            try:
                from places.models import Place

                results['places'] = list(
                    Place.objects.filter(
                        Q(name__icontains=q) | Q(city__icontains=q) | Q(description__icontains=q)
                    ).values('id', 'name', 'city')[:20]
                )
            except Exception:
                results['places'] = []

    return render(request, 'MyTrip/search.html', {'q': q, 'category': category, 'results': results})


def subscribe(request):
    """Handle newsletter subscription from footer."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            try:
                from core.models import Newsletter
                Newsletter.objects.get_or_create(email=email)
                messages.success(request, 'Thank you for subscribing!')
            except Exception as e:
                messages.error(request, 'Subscription failed. Please try again.')
        else:
            messages.error(request, 'Please enter a valid email.')
    
    return redirect(request.META.get('HTTP_REFERER', '/'))