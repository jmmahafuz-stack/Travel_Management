import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a Django admin account from environment variables if one does not already exist."

    def handle(self, *args, **options):
        username = (os.environ.get("ADMIN_USERNAME") or "").strip()
        email = (os.environ.get("ADMIN_EMAIL") or "").strip()
        password = (os.environ.get("ADMIN_PASSWORD") or "").strip()

        if not username or not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping admin creation: ADMIN_USERNAME, ADMIN_EMAIL, and ADMIN_PASSWORD must all be set."
                )
            )
            return

        User = get_user_model()

        # Never overwrite an existing admin or an account with the same username/email.
        existing_admin = User.objects.filter(is_superuser=True).first()
        if existing_admin:
            self.stdout.write(
                self.style.WARNING(
                    f"A superuser already exists ({existing_admin.username}). Skipping admin creation."
                )
            )
            return

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(
                    "An account with the configured admin username or email already exists. Skipping creation."
                )
            )
            return

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True,
            role="admin",
        )

        self.stdout.write(
            self.style.SUCCESS(f"Admin user created successfully: {user.username} ({user.email})")
        )
