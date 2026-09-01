from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserSerializer
from .models import User

# Django template-based auth imports
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import user_passes_test
from .decorators import user_required
from django.db.models import Q, Sum


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ---------------------------------------------------------------------------
# Template-based authentication and dashboard views (added for UI)
# These are additive and do not remove the existing REST API endpoints.
# ---------------------------------------------------------------------------


def register_view(request):
    """Render registration form and create new users.

    Fields: name, email, password, confirm_password
    """

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not email or not password:
            messages.error(request, 'Please provide email and password.')
            return render(request, 'auth/register.html')

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/register.html', {'name': name, 'email': email})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'A user with that email already exists.')
            return render(request, 'auth/register.html', {'name': name, 'email': email})

        # split name into first/last
        first_name = ''
        last_name = ''
        if name:
            parts = name.split()
            first_name = parts[0]
            last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

        # Use email as username to satisfy AbstractUser requirements
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.role = 'user'
        user.save()

        messages.success(request, 'Registration successful. Please log in.')
        return redirect('login')

    return render(request, 'auth/register.html')


def login_view(request):
    """Simple email-based login view with 'remember me' support.

    This view authenticates users by email (the project uses email as unique
    identifier) and creates a session. Admin users are redirected to the
    admin dashboard; regular users to their user dashboard.
    """

    if request.method == 'POST':
        identifier = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember') == 'on'

        user = None
        if identifier and password:
            user = User.objects.filter(
                Q(email=identifier.lower()) | Q(username=identifier)
            ).first()

        if user and user.is_active and user.check_password(password):
            auth_login(request, user)
            # Session expiry: persistent if remember checked, else browser-close
            if remember:
                request.session.set_expiry(1209600)  # two weeks
            else:
                request.session.set_expiry(0)

            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            # Any Django admin-capable account uses the admin panel.
            if user.is_staff or user.is_superuser or getattr(user, 'role', '') == 'admin':
                # Ensure staff flag for Django admin access; keep existing role semantics.
                if not user.is_staff:
                    user.is_staff = True
                    user.save(update_fields=['is_staff'])
                return redirect('admin-home')
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
                return redirect(next_url)
            return redirect('user_dashboard')

        messages.error(request, 'Invalid login credentials.')

    return render(request, 'auth/login.html', {'next': request.GET.get('next', '')})


def logout_view(request):
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    # Render a small post-logout page that offers login links for user or admin.
    return render(request, 'auth/logged_out.html')


def _is_admin(user):
    return user.is_authenticated and getattr(user, 'role', '') == 'admin'


@user_required
def user_dashboard(request):
    """A lightweight user dashboard showing profile and simple counts."""

    # Basic counts and placeholders
    try:
        from bookings.models import FlightBooking, HotelBooking, PackageBooking
        from plans.models import TravelPlan
        flight_count = FlightBooking.objects.filter(user=request.user).count()
        hotel_count = HotelBooking.objects.filter(user=request.user).count()
        package_count = PackageBooking.objects.filter(user=request.user).count()
        # Recent booked packages and saved trip plans
        flight_bookings = FlightBooking.objects.filter(user=request.user).select_related('flight__airline').order_by('-created_at')[:6]
        hotel_bookings = HotelBooking.objects.filter(user=request.user).select_related('hotel').order_by('-created_at')[:6]
        package_bookings = PackageBooking.objects.filter(user=request.user).select_related('package').order_by('-created_at')[:6]
        plans = TravelPlan.objects.filter(user=request.user).order_by('-created_at')[:6]
    except Exception:
        flight_count = hotel_count = package_count = 0
        flight_bookings = []
        hotel_bookings = []
        package_bookings = []
        plans = []

    context = {
        'user': request.user,
        'flight_count': flight_count,
        'hotel_count': hotel_count,
        'package_count': package_count,
        'flight_bookings': flight_bookings,
        'hotel_bookings': hotel_bookings,
        'package_bookings': package_bookings,
        'plans': plans,
    }
    return render(request, 'user/dashboard.html', context)


@user_passes_test(_is_admin)
def admin_dashboard(request):
    """Deprecated custom admin dashboard — redirect to Django admin index."""
    # Keep the view for backward-compatibility but send admins to the main Django admin.
    return redirect('admin:index')
