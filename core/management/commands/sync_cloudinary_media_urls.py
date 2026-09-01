import os

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import ImageField


class Command(BaseCommand):
    help = "Convert old local media URLs in the database to Cloudinary URLs in production."

    def handle(self, *args, **options):
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', '').strip()
        if not cloud_name:
            self.stdout.write(
                self.style.WARNING(
                    'CLOUDINARY_CLOUD_NAME is not set. Skipping Cloudinary URL migration.'
                )
            )
            return

        updated = 0
        checked = 0

        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                for field in model._meta.get_fields():
                    if not isinstance(field, ImageField):
                        continue

                    qs = model.objects.exclude(**{f'{field.name}__isnull': True}).exclude(**{f'{field.name}': ''})
                    for obj in qs:
                        checked += 1
                        value = getattr(obj, field.name)
                        if not value:
                            continue

                        url = value.url if hasattr(value, 'url') else str(value)
                        if 'cloudinary.com' in url or 'res.cloudinary.com' in url:
                            continue

                        name = value.name.strip('/') if getattr(value, 'name', '') else ''
                        if not name:
                            continue

                        cloudinary_url = f'https://res.cloudinary.com/{cloud_name}/image/upload/{name}'
                        setattr(obj, field.name, cloudinary_url)
                        obj.save(update_fields=[field.name])
                        updated += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Updated {model._meta.label}.{field.name} #{obj.pk} -> {cloudinary_url}'
                            )
                        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Checked {checked} image field values; updated {updated} local media URLs to Cloudinary URLs.'
            )
        )
