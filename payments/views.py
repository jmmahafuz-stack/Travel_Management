"""
Views for the payments app.
"""

from rest_framework import viewsets

from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages


@login_required
def mock_process_payment(request):
    """Simple mock payment endpoint.

    POST params: booking_type, booking_id
    Creates a Payment with status 'paid' while leaving the booking in 'pending'
    until an admin verifies and confirms it.
    """
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    booking_type = request.POST.get('booking_type')
    booking_id = request.POST.get('booking_id')
    if not booking_type or not booking_id:
        return JsonResponse({'detail': 'booking_type and booking_id required'}, status=400)

    try:
        booking_id = int(booking_id)
    except ValueError:
        return JsonResponse({'detail': 'invalid booking_id'}, status=400)

    # Resolve booking model
    booking_obj = None
    if booking_type == 'package':
        from bookings.models import PackageBooking
        booking_obj = get_object_or_404(PackageBooking, pk=booking_id)
    elif booking_type == 'flight':
        from bookings.models import FlightBooking
        booking_obj = get_object_or_404(FlightBooking, pk=booking_id)
    elif booking_type == 'hotel':
        from bookings.models import HotelBooking
        booking_obj = get_object_or_404(HotelBooking, pk=booking_id)
    elif booking_type == 'plan':
        from bookings.models import PlanBooking
        booking_obj = get_object_or_404(PlanBooking, pk=booking_id)
    else:
        return JsonResponse({'detail': 'unknown booking_type'}, status=400)

    # Ensure the requesting user owns the booking or is admin
    if booking_obj.user != request.user and getattr(request.user, 'role', '') != 'admin':
        return JsonResponse({'detail': 'permission denied'}, status=403)

    # Create payment and mark booking confirmed
    import uuid as _uuid
    transaction_id = f"MOCK-{_uuid.uuid4().hex[:12]}"
    payment = Payment.objects.create(
        user=request.user,
        booking_type=booking_type,
        booking_id=booking_obj.id,
        amount=getattr(booking_obj, 'total_price', 0) or 0,
        transaction_id=transaction_id,
        payment_status='paid',
    )
    # Do NOT automatically confirm the booking here — admin must approve after payment.
    return JsonResponse({'detail': 'payment processed', 'payment_id': payment.id})


@login_required
def checkout_process(request):
    """Process a checkout form POST from the site and redirect back to bookings.

    Expects POST: booking_type, booking_id
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request')
        return redirect('bookings_page')

    booking_type = request.POST.get('booking_type')
    booking_id = request.POST.get('booking_id')
    if not booking_type or not booking_id:
        messages.error(request, 'Missing booking information')
        return redirect('bookings_page')

    try:
        booking_id = int(booking_id)
    except ValueError:
        messages.error(request, 'Invalid booking id')
        return redirect('bookings_page')

    booking_obj = None
    if booking_type == 'package':
        from bookings.models import PackageBooking
        booking_obj = get_object_or_404(PackageBooking, pk=booking_id)
    elif booking_type == 'flight':
        from bookings.models import FlightBooking
        booking_obj = get_object_or_404(FlightBooking, pk=booking_id)
    elif booking_type == 'hotel':
        from bookings.models import HotelBooking
        booking_obj = get_object_or_404(HotelBooking, pk=booking_id)
    elif booking_type == 'plan':
        from bookings.models import PlanBooking
        booking_obj = get_object_or_404(PlanBooking, pk=booking_id)
    else:
        messages.error(request, 'Unknown booking type')
        return redirect('bookings_page')

    if booking_obj.user != request.user and getattr(request.user, 'role', '') != 'admin':
        messages.error(request, 'Permission denied')
        return redirect('bookings_page')

    # create payment record using posted transaction details (user-supplied)
    transaction_number = request.POST.get('transaction_number')
    payer_name = request.POST.get('payer_name')
    import uuid as _uuid
    from .models import Payment
    if transaction_number:
        # include payer name in the stored transaction id for minimal auditability
        if payer_name:
            transaction_id = f"{transaction_number} | {payer_name}"
        else:
            transaction_id = transaction_number
    else:
        transaction_id = f"MOCK-{_uuid.uuid4().hex[:12]}"

    # Payment is considered confirmed immediately, but the booking itself remains
    # pending until an admin validates the payment and confirms the booking.
    payment = Payment.objects.create(
        user=request.user,
        booking_type=booking_type,
        booking_id=booking_obj.id,
        amount=getattr(booking_obj, 'total_price', 0) or 0,
        transaction_id=transaction_id,
        payment_status='paid',
    )

    # Keep booking pending until admin approval; it still needs to appear in My Bookings.
    try:
        booking_obj.booking_status = 'pending'
        booking_obj.save()
    except Exception:
        pass

    # If this was an AJAX request, return JSON so the frontend can update in-place.
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'payment_id': payment.id})

    messages.success(request, 'Payment recorded successfully. Booking remains pending until admin confirms after reviewing the payment.')
    return redirect('bookings_page')
