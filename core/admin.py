"""
Minimal admin for the core app.
"""

from django.contrib import admin

# Core has no models by default; this file is a safe placeholder.

# Hide auth Group from admin index so the "Authentication" app doesn't
# appear on the admin homepage. This runs when admin modules are imported.
from django.contrib.auth.models import Group
try:
	admin.site.unregister(Group)
except Exception:
	pass


# Register SiteOption admin here if the model exists.
try:
	from .models import SiteOption

	@admin.register(SiteOption)
	class SiteOptionAdmin(admin.ModelAdmin):
		list_display = ('hero_heading', 'updated_at')
		readonly_fields = ('updated_at',)
		fieldsets = (
			('Home Page Hero', {
				'fields': ('hero_image', 'hero_heading', 'hero_subheading', 'search_placeholder'),
				'description': 'Customize the homepage hero section'
			}),
			('Header Styling', {
				'fields': ('header_image', 'header_color', 'header_text_color'),
				'description': 'Customize the header background image and colors. Leave header_image blank to use header_color.'
			}),
			('Footer Styling', {
				'fields': ('footer_image', 'footer_color', 'footer_text_color'),
				'description': 'Customize the footer background image and colors. Leave footer_image blank to use footer_color.'
			}),
			('Metadata', {
				'fields': ('updated_at',),
				'classes': ('collapse',)
			}),
		)

		def has_add_permission(self, request):
			# Only allow a single SiteOption instance for simplicity.
			if SiteOption.objects.exists():
				return False
			return super().has_add_permission(request)
except Exception:
	# If the model isn't present (migrations not applied) skip registration.
	pass


# Register Newsletter admin here if the model exists.
try:
	from .models import Newsletter

	@admin.register(Newsletter)
	class NewsletterAdmin(admin.ModelAdmin):
		list_display = ('email', 'subscribed_at')
		readonly_fields = ('subscribed_at',)
		search_fields = ('email',)
		list_filter = ('subscribed_at',)
		date_hierarchy = 'subscribed_at'
except Exception:
	# If the model isn't present (migrations not applied) skip registration.
	pass
