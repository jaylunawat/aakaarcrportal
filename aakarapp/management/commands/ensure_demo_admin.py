import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the initial administrator from environment variables when configured."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")

        configured_values = (username, email, password)
        if not any(configured_values):
            self.stdout.write("Demo administrator variables are not configured; skipping.")
            return
        if not all(configured_values):
            raise CommandError(
                "Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and "
                "DJANGO_SUPERUSER_PASSWORD together."
            )

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )

        changed_fields = []
        user.set_password(password)
        changed_fields.append("password")
        if user.email != email:
            user.email = email
            changed_fields.append("email")
        if not user.is_staff:
            user.is_staff = True
            changed_fields.append("is_staff")
        if not user.is_superuser:
            user.is_superuser = True
            changed_fields.append("is_superuser")
        user.save(update_fields=changed_fields)
        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f'{action} administrator "{username}".'))
