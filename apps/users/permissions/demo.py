from django.utils import timezone
from rest_framework.permissions import BasePermission


class IsActiveDemo(BasePermission):
    """
    Allows access only to active authenticated demo users whose
    demo_expires_at has not passed.
    """

    message = "You must be a demo user with an active demo session."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        if not getattr(user, "is_demo", False):
            self.message = "You must be a demo user to perform this action."
            return False

        demo_expires_at = getattr(user, "demo_expires_at", None)
        if not demo_expires_at:
            # Missing expiry field on a demo user is considered a configuration issue
            self.message = "Demo account missing expiration info."
            return False

        if (
            callable(getattr(user, "is_demo_expired", None)) and user.is_demo_expired()
        ) or demo_expires_at <= timezone.now():
            self.message = (
                "Your demo account has expired. Please create a new demo user."
            )
            return False

        return True
