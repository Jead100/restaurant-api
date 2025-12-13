from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Delete demo users whose demo_expires_at is in the past."

    def handle(self, *args, **options):
        qs = User.objects.expired_demos()
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted expired demo users: {count}"))
