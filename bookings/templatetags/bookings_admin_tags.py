from django import template
from django.apps import apps
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def pending_count(app_label, model_name):
    """Return count of objects with booking_status='pending' for the given model.

    Returns 0 if the model doesn't exist or doesn't have the field.
    """
    try:
        model = apps.get_model(app_label, model_name)
        # Only count if the model has booking_status field
        if hasattr(model, 'objects'):
            qs = model.objects.filter(booking_status='pending')
            return qs.count()
    except Exception:
        pass
    return 0


@register.simple_tag
def pending_badge(app_label, model_name):
    """Return HTML for a pending-count badge or empty string if zero/error."""
    try:
        model = apps.get_model(app_label, model_name)
        if hasattr(model, 'objects'):
            cnt = model.objects.filter(booking_status='pending').count()
            if cnt:
                return format_html('<span class="pending-badge" title="{} pending">{}</span>', cnt, cnt)
    except Exception:
        pass
    return ''


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary using the given key.
    
    Usage: {{ payment_map|get_item:"flight_123" }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
