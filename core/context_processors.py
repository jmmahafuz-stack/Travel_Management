from .models import SiteOption


def _safe_file_url(field):
    """Return the file URL for a FieldFile or None if not present.

    Accessing `.url` on a FieldFile raises ValueError when no file is
    associated; this helper guards that access.
    """
    if not field:
        return None
    name = getattr(field, 'name', None)
    if not name:
        return None
    try:
        return field.url
    except Exception:
        return None


def site_options(request):
    """Expose a single SiteOption instance and common fields to templates.

    Returns a dict with `site_option` plus convenience keys for hero/footer
    images and texts so templates can easily access them without requiring
    each view to pass the object.
    """
    try:
        opt = SiteOption.objects.first()
    except Exception:
        opt = None

    return {
        'site_option': opt,
        'hero_image': _safe_file_url(getattr(opt, 'hero_image', None)) if opt else None,
        'footer_image': _safe_file_url(getattr(opt, 'footer_image', None)) if opt else None,
        'header_image': _safe_file_url(getattr(opt, 'header_image', None)) if opt else None,
        'hero_heading': opt.hero_heading if opt else None,
        'hero_subheading': opt.hero_subheading if opt else None,
        'search_placeholder': opt.search_placeholder if opt else None,
        'header_color': opt.header_color if opt else '#1e40af',
        'header_text_color': opt.header_text_color if opt else '#ffffff',
        'footer_color': opt.footer_color if opt else '#1e40af',
        'footer_text_color': opt.footer_text_color if opt else '#ffffff',
    }
