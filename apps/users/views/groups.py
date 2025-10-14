from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from apps.core.pagination import CustomPageNumberPagination
from apps.core.responses import format_response
from apps.restaurant.models import Order

from ..permissions import IsManager
from ..viewsets import GroupMembershipViewSet


class ManagerGroupViewSet(GroupMembershipViewSet):
    """
    Viewset for managing users in the 'Manager' group.

    Only managers can list, add, retrieve, or remove users
    from the group.
    """

    group_name = "Manager"

    permission_classes = [IsAuthenticated, IsManager]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    pagination_class = CustomPageNumberPagination

    resource_name = "Manager"


class DeliveryCrewGroupViewSet(GroupMembershipViewSet):
    """
    Viewset for managing users in the 'Delivery crew' group.

    Only managers can add, retrieve, list, or remove delivery crew members.
    """

    group_name = "Delivery crew"

    permission_classes = [IsAuthenticated, IsManager]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    pagination_class = CustomPageNumberPagination

    resource_name = "Delivery crew member"

    def destroy(self, request, *args, **kwargs):
        """
        Remove a delivery crew member and unassign them from any orders.

        Overrides the parent method to clear the `delivery_crew` field
        on all orders assigned to the user before group removal.
        """
        user = self.get_object()
        Order.objects.filter(delivery_crew=user).update(delivery_crew=None)
        self.group.user_set.remove(user)
        return format_response(
            detail=(
                f"User '{user.username}' successfully removed "
                f"from the {self.group_name} group."
            ),
            data=None,
            status=status.HTTP_200_OK,
        )
