from django.db import models
from django.utils import timezone


class DemoUserMixin(models.Model):
    """
    Abtract mixin that provides demo-related fields and utilities
    for temporary demo accounts.
    """

    is_demo = models.BooleanField(default=False, db_index=True)
    demo_expires_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    def is_demo_expired(self) -> bool:
        return (
            self.is_demo
            and self.demo_expires_at
            and self.demo_expires_at < timezone.now()
        )

    def is_demo_active(self) -> bool:
        return self.is_demo and not self.is_demo_expired()


class DemoUserQuerySet(models.QuerySet):
    """
    Adds reusable filters for demo-related model queries.
    Suitable for models defining `is_demo` and `demo_expires_at` (e.g., DemoUserMixin).
    """

    def demos(self):
        return self.filter(is_demo=True)

    def active_demos(self):
        return self.filter(
            is_demo=True,
            demo_expires_at__isnull=False,
            demo_expires_at__gt=timezone.now(),
        )

    def expired_demos(self):
        return self.filter(
            is_demo=True,
            demo_expires_at__isnull=False,
            demo_expires_at__lt=timezone.now(),
        )

    def non_demos(self):
        return self.filter(is_demo=False)
