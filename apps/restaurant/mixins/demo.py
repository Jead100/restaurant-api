from rest_framework.exceptions import PermissionDenied

from apps.users.mixins import DemoUserAccessMixin


class RestaurantDemoGuardMixin(DemoUserAccessMixin):
    """
    Enforces demo-mode restrictions for restaurant-related views.
    """

    def perform_create(self, serializer):
        """
        Mark created objects as demo data when demo mode is enabled.
        """
        if self._is_demo_mode_enabled():
            serializer.save(is_demo=True)
        else:
            serializer.save()

    def perform_update(self, serializer):
        """
        Restrict updates to demo objects when demo mode is enabled.
        """
        if self._is_demo_mode_enabled():
            instance = self.get_object()
            if not instance.is_demo:
                raise PermissionDenied("Cannot modify production data in demo mode.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Restrict deletes to demo objects when demo mode is enabled.
        """
        if self._is_demo_mode_enabled() and not instance.is_demo:
            raise PermissionDenied("Cannot delete production data in demo mode.")
        instance.delete()
