"""
Basic views for the dashboard app.

These are minimal placeholders to make it easier to extend later.
"""

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from flights.models import Flight
from hotels.models import Hotel
from packages.models import Package
from accounts.models import User
from bookings.models import FlightBooking, HotelBooking, PackageBooking

from .forms import FlightForm, HotelForm, PackageForm


def health_check(request):
    """Simple health endpoint used during setup and tests."""

    return JsonResponse({"status": "ok", "app": "dashboard"})


def _is_admin(user):
    """Check if user is an admin (via role or staff/superuser status)."""
    return user.is_authenticated and (
        getattr(user, 'role', '') == 'admin' or 
        user.is_staff or 
        user.is_superuser
    )


@login_required
def admin_home(request):
    """Admin home page with unified dashboard and admin panel access."""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    
    # Get statistics
    total_users = User.objects.count()
    total_flights = Flight.objects.count()
    total_hotels = Hotel.objects.count()
    total_packages = Package.objects.count()
    
    # Booking statistics
    total_bookings = (
        FlightBooking.objects.count() + 
        HotelBooking.objects.count() + 
        PackageBooking.objects.count()
    )
    
    pending_bookings = (
        FlightBooking.objects.filter(booking_status='pending').count() + 
        HotelBooking.objects.filter(booking_status='pending').count() + 
        PackageBooking.objects.filter(booking_status='pending').count()
    )
    
    # Revenue calculation
    flight_revenue = FlightBooking.objects.filter(
        booking_status='confirmed'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    hotel_revenue = HotelBooking.objects.filter(
        booking_status='confirmed'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    package_revenue = PackageBooking.objects.filter(
        booking_status='confirmed'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    total_revenue = flight_revenue + hotel_revenue + package_revenue
    
    # Recent bookings
    recent_bookings = []
    flight_bookings = FlightBooking.objects.select_related('user', 'flight').order_by('-created_at')[:3]
    hotel_bookings = HotelBooking.objects.select_related('user', 'hotel').order_by('-created_at')[:3]
    package_bookings = PackageBooking.objects.select_related('user', 'package').order_by('-created_at')[:3]
    
    context = {
        'total_users': total_users,
        'total_flights': total_flights,
        'total_hotels': total_hotels,
        'total_packages': total_packages,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'total_revenue': total_revenue,
        'recent_flight_bookings': flight_bookings,
        'recent_hotel_bookings': hotel_bookings,
        'recent_package_bookings': package_bookings,
    }
    
    return render(request, 'dashboard/admin_home.html', context)


def flights_list(request):
    flights = Flight.objects.select_related('airline').all().order_by('-created_at')
    return render(request, 'dashboard/flights_list.html', {'flights': flights})


@user_passes_test(_is_admin)
def flight_create(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard-manage-flights')
    else:
        form = FlightForm()
    return render(request, 'dashboard/flight_form.html', {'form': form, 'title': 'Add Flight'})


@user_passes_test(_is_admin)
def flight_edit(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            return redirect('dashboard-manage-flights')
    else:
        form = FlightForm(instance=flight)
    return render(request, 'dashboard/flight_form.html', {'form': form, 'title': 'Edit Flight'})


@user_passes_test(_is_admin)
def flight_delete(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    if request.method == 'POST':
        flight.delete()
        return redirect('dashboard-manage-flights')
    return render(request, 'dashboard/confirm_delete.html', {'object': flight, 'type': 'Flight'})


@user_passes_test(_is_admin)
def hotels_list(request):
    hotels = Hotel.objects.all().order_by('name')
    return render(request, 'dashboard/hotels_list.html', {'hotels': hotels})


@user_passes_test(_is_admin)
def hotel_create(request):
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard-manage-hotels')
    else:
        form = HotelForm()
    return render(request, 'dashboard/hotel_form.html', {'form': form, 'title': 'Add Hotel'})


@user_passes_test(_is_admin)
def hotel_edit(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            return redirect('dashboard-manage-hotels')
    else:
        form = HotelForm(instance=hotel)
    return render(request, 'dashboard/hotel_form.html', {'form': form, 'title': 'Edit Hotel'})


@user_passes_test(_is_admin)
def hotel_delete(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == 'POST':
        hotel.delete()
        return redirect('dashboard-manage-hotels')
    return render(request, 'dashboard/confirm_delete.html', {'object': hotel, 'type': 'Hotel'})


@user_passes_test(_is_admin)
def packages_list(request):
    packages = Package.objects.all().order_by('-id')
    return render(request, 'dashboard/packages_list.html', {'packages': packages})


@user_passes_test(_is_admin)
def package_create(request):
    if request.method == 'POST':
        form = PackageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard-manage-packages')
    else:
        form = PackageForm()
    return render(request, 'dashboard/package_form.html', {'form': form, 'title': 'Add Package'})


@user_passes_test(_is_admin)
def package_edit(request, pk):
    pkg = get_object_or_404(Package, pk=pk)
    if request.method == 'POST':
        form = PackageForm(request.POST, instance=pkg)
        if form.is_valid():
            form.save()
            return redirect('dashboard-manage-packages')
    else:
        form = PackageForm(instance=pkg)
    return render(request, 'dashboard/package_form.html', {'form': form, 'title': 'Edit Package'})


@user_passes_test(_is_admin)
def package_delete(request, pk):
    pkg = get_object_or_404(Package, pk=pk)
    if request.method == 'POST':
        pkg.delete()
        return redirect('dashboard-manage-packages')
    return render(request, 'dashboard/confirm_delete.html', {'object': pkg, 'type': 'Package'})


@user_passes_test(_is_admin)
@user_passes_test(_is_admin)
def bookings_list(request):
    from bookings.models import FlightBooking, HotelBooking, PackageBooking

    flight_bookings = FlightBooking.objects.select_related('flight', 'user').all().order_by('-created_at')
    hotel_bookings = HotelBooking.objects.select_related('hotel', 'user').all().order_by('-created_at')
    package_bookings = PackageBooking.objects.select_related('package', 'user').all().order_by('-created_at')

    return render(request, 'dashboard/bookings_list.html', {
        'flight_bookings': flight_bookings,
        'hotel_bookings': hotel_bookings,
        'package_bookings': package_bookings,
    })


@user_passes_test(_is_admin)
def booking_action(request, btype, pk, action):
    """Perform an action on a booking: confirm or cancel."""
    from payments.models import Payment
    
    model = None
    if btype == 'flight':
        from bookings.models import FlightBooking
        model = FlightBooking
    elif btype == 'hotel':
        from bookings.models import HotelBooking
        model = HotelBooking
    elif btype == 'package':
        from bookings.models import PackageBooking
        model = PackageBooking
    else:
        messages.error(request, 'Invalid booking type.')
        return redirect('dashboard-manage-bookings')

    booking = get_object_or_404(model, pk=pk)
    
    if action == 'confirm':
        # Check if payment exists and is paid
        payment = Payment.objects.filter(booking_type=btype, booking_id=pk).first()
        
        if not payment:
            messages.warning(request, f"No payment found for this booking. Please process payment first.")
            return redirect('dashboard-manage-bookings')
        
        if payment.payment_status != 'paid':
            messages.warning(request, f"Payment status is '{payment.payment_status}'. Only 'paid' payments can be confirmed.")
            return redirect('dashboard-manage-bookings')
        
        # Confirm the booking
        booking.booking_status = 'confirmed'
        booking.save()
        messages.success(request, f"✓ Booking #{booking.id} confirmed successfully! Payment ID: {payment.id}")
        
        # Send confirmation email to user
        try:
            recipient = booking.user.email if getattr(booking.user, 'email', '') else None
            if recipient:
                subject = f"Booking Confirmation - MyTrip #{booking.id}"
                message = f"""Dear {booking.user.first_name or booking.user.username},

Your booking has been confirmed by our admin team.

Booking Details:
- Booking ID: {booking.id}
- Type: {btype.capitalize()}
- Status: CONFIRMED
- Payment ID: {payment.id}
- Amount: ৳{payment.amount}

Thank you for booking with MyTrip!

Best regards,
MyTrip Team"""
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@mytrip.local')
                send_mail(subject, message, from_email, [recipient], fail_silently=True)
                messages.info(request, f"Confirmation email sent to {recipient}")
        except Exception as e:
            messages.warning(request, "Could not send confirmation email to user.")
            
    elif action == 'cancel':
        # Cancel the booking
        booking.booking_status = 'cancelled'
        booking.save()
        messages.success(request, f"✓ Booking #{booking.id} cancelled successfully.")
        
        # Send cancellation email to user
        try:
            recipient = booking.user.email if getattr(booking.user, 'email', '') else None
            if recipient:
                subject = f"Booking Cancelled - MyTrip #{booking.id}"
                message = f"""Dear {booking.user.first_name or booking.user.username},

Your booking has been cancelled by our admin team.

Booking ID: {booking.id}
Type: {btype.capitalize()}
Status: CANCELLED

If you believe this is a mistake, please contact our support team.

Best regards,
MyTrip Team"""
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@mytrip.local')
                send_mail(subject, message, from_email, [recipient], fail_silently=True)
                messages.info(request, f"Cancellation email sent to {recipient}")
        except Exception as e:
            messages.warning(request, "Could not send cancellation email to user.")
    else:
        messages.error(request, 'Invalid action.')
        return redirect('dashboard-manage-bookings')

    return redirect('dashboard-manage-bookings')


@user_passes_test(_is_admin)
def profile_edit(request):
    """Allow admin users to edit their name and change password (requires current password)."""
    user = request.user
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        old_password = request.POST.get('old_password', '')
        new_password1 = request.POST.get('new_password1', '')
        new_password2 = request.POST.get('new_password2', '')

        errors = []
        # If attempting a password change, validate current password and matching
        if new_password1 or new_password2:
            if not old_password:
                errors.append('Please enter your current password to change password.')
            elif not user.check_password(old_password):
                errors.append('Current password is incorrect.')
            elif new_password1 != new_password2:
                errors.append('New passwords do not match.')
            else:
                # validate password strength using Django validators
                from django.contrib.auth.password_validation import validate_password
                try:
                    validate_password(new_password1, user)
                except Exception as e:
                    errors.append(str(e))

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'dashboard/profile_edit.html', {'user_obj': user})

        # Apply changes
        user.first_name = first_name
        user.last_name = last_name
        if new_password1:
            user.set_password(new_password1)
        user.save()

        # Keep the session authenticated if password changed
        if new_password1:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)

        messages.success(request, 'Profile updated successfully.')
        return redirect('admin:index')

    return render(request, 'dashboard/profile_edit.html', {'user_obj': user})
    return render(request, 'dashboard/profile_edit.html', {'user_obj': user})
