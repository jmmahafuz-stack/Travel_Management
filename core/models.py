"""Core site models.

This module contains a small `SiteOption` model used to manage simple
site-wide settings editable via the admin UI (homepage hero image, texts,
and search placeholder).
"""

from django.db import models


class SiteOption(models.Model):
	"""Simple singleton settings for the public site.

	Admins can add/edit a single `SiteOption` instance to customize the
	homepage hero background image, heading, subheading and search
	placeholder text.
	"""
	hero_image = models.ImageField(upload_to='site/', blank=True, null=True)
	hero_heading = models.CharField(max_length=200, blank=True, default='Travel better with MyTrip')
	hero_subheading = models.TextField(blank=True, default='Search flights, hotels and curated travel packages — plan and book in a few clicks.')
	search_placeholder = models.CharField(max_length=200, blank=True, default='Search destinations, flights, hotels...')
	
	# Header customization
	header_image = models.ImageField(upload_to='site/', blank=True, null=True, help_text='Header background image. If not set, uses header_color.')
	header_color = models.CharField(max_length=7, blank=True, default='#1e40af', help_text='Header background color (hex format, e.g. #1e40af)')
	header_text_color = models.CharField(max_length=7, blank=True, default='#ffffff', help_text='Header text color (hex format, e.g. #ffffff)')
	
	# Footer customization
	footer_image = models.ImageField(upload_to='site/', blank=True, null=True, help_text='Footer background image. If not set, uses footer_color.')
	footer_color = models.CharField(max_length=7, blank=True, default='#1e40af', help_text='Footer background color (hex format, e.g. #1e40af)')
	footer_text_color = models.CharField(max_length=7, blank=True, default='#ffffff', help_text='Footer text color (hex format, e.g. #ffffff)')
	
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return 'Site Settings'

	class Meta:
		verbose_name = 'Site Setting'
		verbose_name_plural = 'Site Settings'


class Newsletter(models.Model):
	"""Newsletter subscription model."""
	email = models.EmailField(unique=True)
	subscribed_at = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.email
	
	class Meta:
		verbose_name = 'Newsletter Subscriber'
		verbose_name_plural = 'Newsletter Subscribers'
