from django.conf import settings
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsActiveDemo


class DemoUserAccessMixin:
    """
    Enforces demo-user-specific permissions for views when demo mode is enabled.
    """

    def _is_demo_mode_enabled(self):
        """
        Return True if demo mode is enabled in settings.
        """
        return getattr(settings, "DEMO_MODE", False)

    def get_permissions(self):
        """
        Modify the view's permission list to enforce active demo-user access.

        When demo mode is enabled, active demo users must also satisfy
        the `IsActiveDemo` permission. Non-demo users retain normal access.
        """
        # Start with the permissions explicitly declared on the view
        perms = list(getattr(self, "permission_classes", []))

        user = getattr(getattr(self, "request", None), "user", None)

        # In demo mode, enforce IsActiveDemo for demo users
        if self._is_demo_mode_enabled() and getattr(user, "is_demo", False):
            # Insert IsActiveDemo after IsAuthenticated if it is the first permission,
            # otherwise insert it at the beginning
            if IsActiveDemo not in perms:
                insert_pos = 1 if perms and perms[0] == IsAuthenticated else 0
                perms.insert(insert_pos, IsActiveDemo)

        self.permission_classes = perms
        return super().get_permissions()


class GroupDemoGuardMixin(DemoUserAccessMixin):
    """
    Enforces demo-user restrictions on adding or removing users
    within group management views.
    """

    def perform_create(self, serializer):
        """
        Restrict demo users to adding only other demo users.
        """
        user = serializer.validated_data["user"]
        if self._is_demo_mode_enabled() and not getattr(user, "is_demo", False):
            raise PermissionDenied("Demo users can only add other demo users.")
        self.group.user_set.add(user)

    def perform_destroy(self, instance):
        """
        Restrict demo users to removing only other demo users.
        """
        user = instance
        if self._is_demo_mode_enabled() and not getattr(user, "is_demo", False):
            raise PermissionDenied("Demo users can only remove other demo users.")
        self.group.user_set.remove(user)
