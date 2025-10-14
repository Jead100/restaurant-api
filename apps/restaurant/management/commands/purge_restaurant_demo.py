from django.core.management.base import BaseCommand
from django.db import transaction
from apps.restaurant.models import Order, Cart, MenuItem, Category


class Command(BaseCommand):
    help = "Hard-purge of ALL demo rows (is_demo=True) in the restaurant app."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Show counts only")

    def handle(self, *args, **opts):
        dry = opts["dry_run"]
        say = self.stdout.write

        say("Starting demo purge (Orders → Carts → MenuItems → Categories)...")
        with transaction.atomic():
            # 1) Orders (demo)
            q = Order.objects.filter(is_demo=True)
            n = q.count()
            if dry:
                say(f"[DRY] Orders: {n} would be deleted")
            else:
                q.delete() or say(f"Orders deleted: {n}")

            # 2) Cart lines (demo)
            q = Cart.objects.filter(is_demo=True)
            n = q.count()
            if dry:
                say(f"[DRY] Cart lines: {n} would be deleted")
            else:
                q.delete() or say(f"Cart lines deleted: {n}")

            # 3) MenuItems (demo)
            q = MenuItem.objects.filter(is_demo=True)
            n = q.count()
            if dry:
                say(f"[DRY] MenuItems: {n} would be deleted")
            else:
                q.delete() or say(f"MenuItems deleted: {n}")

            # 4) Categories (demo)
            q = Category.objects.filter(is_demo=True)
            n = q.count()
            if dry:
                say(f"[DRY] Categories: {n} would be deleted")
            else:
                q.delete() or say(f"Categories deleted: {n}")

        self.stdout.write(self.style.SUCCESS("Demo purge complete."))
