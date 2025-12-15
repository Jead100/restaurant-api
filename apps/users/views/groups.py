from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from apps.core.mixins.message import ResponseMessageMixin
from apps.core.pagination import CustomPageNumberPagination
from apps.core.responses import format_response
from apps.restaurant.models import Order

from ..mixins.demo import DemoUserAccessMixin, GroupDemoGuardMixin
from ..permissions import IsManagerOrAdminUser, IsManagerForReadOnlyOrAdminUser
from ..roles import Role
from ..serializers import UserSerializer
from ..viewsets import GroupMembershipViewSet

User = get_user_model()


class ManagerGroupViewSet(
    GroupDemoGuardMixin,  # demo support
    GroupMembershipViewSet,
):
    """
    Viewset for managing users in the 'Manager' group.

    Managers can only list or retrieve users in the group.
    Admin users can do more: list, retrieve, add, or remove managers.
    """

    group_name = str(Role.MANAGER.label)

    permission_classes = [IsAuthenticated, IsManagerForReadOnlyOrAdminUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    pagination_class = CustomPageNumberPagination

    resource_name = "Manager"


class DeliveryCrewGroupViewSet(
    GroupDemoGuardMixin,
    GroupMembershipViewSet,
):
    """
    Viewset for managing users in the 'Delivery crew' group.

    Only managers or admin users can add, retrieve, list,
    or remove delivery crew members.
    """

    group_name = str(Role.DELIVERY_CREW.label)

    permission_classes = [IsAuthenticated, IsManagerOrAdminUser]
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
        self.perform_destroy(user)  # remove from group
        return format_response(
            detail=(
                f"User '{user.username}' successfully removed "
                f"from the {self.group.name} group."
            ),
            data=None,
            status=status.HTTP_200_OK,
        )


class CustomerListAPIView(
    DemoUserAccessMixin,  # demo support
    ResponseMessageMixin,  # for `resource_name` support
    ListAPIView,
):
    """
    API view for listing all customers (i.e., users that don't belong to a group).

    Accessible by authenticated users with manager or admin roles.
    """

    queryset = (
        User.objects.filter(groups__isnull=True)
        .exclude(is_superuser=True)  # exclude admin-level users
        .order_by("id")
    )
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdminUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    pagination_class = CustomPageNumberPagination
    resource_name = "Customer"
