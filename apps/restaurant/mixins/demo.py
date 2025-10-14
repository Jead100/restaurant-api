from django.conf import settings
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsActiveDemo


class DemoScopeMixin:
    """
    Enforces demo mode rules for the restaurant viewsets.

    Useful for demo environments where production data
    (data not marked as demo in this case) must remain intact.

    When `DEMO_MODE` is enabled in settings:
    - IsActiveDemo permission is enforced for demo users.
    - New objects are marked as demo data.
    - Updates and deletes are restricted to demo objects only.
    """

    def _is_demo_mode_enabled(self):
        """
        Return True if demo mode is enabled in settings.
        """
        return getattr(settings, "DEMO_MODE", False)

    def get_permissions(self):
        """
        Modify the view's permission list to enforce active demo user access.

        When demo mode is enabled, active demo users must also satisfy
        the `IsActiveDemo` permission. Non-demo users retain normal access.
        """
        # Start with the permissions explicitly declared on the view
        perms = list(getattr(self, "permission_classes", []))

        user = getattr(getattr(self, "request", None), "user", None)

        # In demo mode, enforce IsActiveDemo for demo users
        if self._is_demo_mode_enabled() and getattr(user, "is_demo", False):
            # insert IsActiveDemo after IsAuthenticated if it is the first permission,
            # otherwise insert it at the beginning
            if IsActiveDemo not in perms:
                insert_pos = 1 if perms and perms[0] == IsAuthenticated else 0
                perms.insert(insert_pos, IsActiveDemo)

        self.permission_classes = perms
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Mark created objects as demo data when in demo mode.
        """
        if self._is_demo_mode_enabled():
            serializer.save(is_demo=True)
        else:
            serializer.save()

    def perform_update(self, serializer):
        """
        Restrict updates to demo objects when in demo mode.
        """
        if self._is_demo_mode_enabled():
            instance = self.get_object()
            if not instance.is_demo:
                raise PermissionDenied("Cannot modify production data in demo mode.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Restrict deletes to demo objects when in demo mode.
        """
        if self._is_demo_mode_enabled() and not instance.is_demo:
            raise PermissionDenied("Cannot delete production data in demo mode.")
        instance.delete()
