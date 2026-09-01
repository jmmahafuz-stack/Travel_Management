"""
URL configuration for travel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from payments import views as payments_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect
from django.urls import reverse

# Customize Django admin site display names
admin.site.site_header = "MyTrip Administration"
admin.site.site_title = "MyTrip Admin"
admin.site.index_title = "MyTrip Administration"

# Apply small admin customizations (hide Group, etc.)
import travel.admin_hide

# Custom admin index that redirects to unified dashboard
@require_http_methods(["GET"])
def admin_index_redirect(request):
    """Redirect admin index to unified admin dashboard."""
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseRedirect(reverse('admin-home'))
    return admin.site.index(request)

# Use the standard admin site (staff users with `is_staff=True` can access `/admin/`).
urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('payments/mock/', payments_views.mock_process_payment, name='mock-payment'),
    path('payments/checkout/process/', payments_views.checkout_process, name='payments-checkout-process'),
    # API routes
    path('api/auth/', include('accounts.urls')),
    path('api/flights/', include('flights.urls')),
    path('api/hotels/', include('hotels.urls')),
    path('api/packages/', include('packages.urls')),
    path('api/places/', include('places.api_urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/payments/', include('payments.urls')),
    path('places/', include('places.urls')),
    # Frontend/site routes
    path('', include('MyTrip.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
