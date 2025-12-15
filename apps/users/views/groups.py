from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)

from apps.core.mixins.message import ResponseMessageMixin
from apps.core.pagination import CustomPageNumberPagination
from apps.core.responses import format_response
from apps.core.schemas import SimpleDetailSerializer
from apps.restaurant.models import Order

from ..mixins.demo import DemoUserAccessMixin, GroupDemoGuardMixin
from ..permissions import IsManagerOrAdminUser, IsManagerForReadOnlyOrAdminUser
from ..roles import Role
from ..schemas import UserEnvelopeSerializer
from ..serializers import UserSerializer
from ..viewsets import GroupMembershipViewSet

User = get_user_model()


@extend_schema(tags=["Role Groups"])
@extend_schema_view(
    list=extend_schema(
        summary="Retrieve a list of manager users.",
        description=(
            "Returns a paginated list of users in the 'Manager' group.\n\n"
            "Only managers and admin users can access this endpoint."
        ),
    ),
    retrieve=extend_schema(
        summary="Retrieve a manager user by ID.",
        description=(
            "Returns details for a single user in the 'Manager' group.\n\n"
            "Only managers and admin users can access this endpoint."
        ),
        responses={200: UserEnvelopeSerializer},
    ),
    create=extend_schema(
        summary="Add a user to the Manager group.",
        description=(
            "Adds the specified user to the 'Manager' group.\n\n"
            "Only admin users can perform this action."
        ),
        responses={201: SimpleDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Remove a user from the Manager group.",
        description=(
            "Removes the specified user from the 'Manager' group.\n\n"
            "Only admin users can perform this action."
        ),
        responses={200: SimpleDetailSerializer},
    ),
)
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


@extend_schema(tags=["Role Groups"])
@extend_schema_view(
    list=extend_schema(
        summary="Retrieve a list of delivery crew users.",
        description=(
            "Returns a paginated list of users in the 'Delivery crew' group.\n\n"
            "Only managers and admin users can access this endpoint."
        ),
    ),
    retrieve=extend_schema(
        summary="Retrieve a delivery crew user by ID.",
        description=(
            "Returns details for a single user in the 'Delivery crew' group.\n\n"
            "Only managers and admin users can access this endpoint."
        ),
        responses={200: UserEnvelopeSerializer},
    ),
    create=extend_schema(
        summary="Add a user to the Delivery crew group.",
        description=(
            "Adds the specified user to the 'Delivery crew' group.\n\n"
            "Only managers and admin users can perform this action."
        ),
        responses={201: SimpleDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Remove a user from the Delivery crew group.",
        description=(
            "Removes the specified user from the 'Delivery crew' group and "
            "clears any orders assigned to them.\n\n"
            "Only managers and admin users can perform this action."
        ),
        responses={200: SimpleDetailSerializer},
    ),
)
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


@extend_schema(
    tags=["Role Groups"],
    summary="Retrieve a list of all customers.",
    description=(
        "Returns a paginated list of customer users (users that do not belong "
        "to any role group and are not superusers).\n\n"
        "Only managers and admin users can access this endpoint."
    ),
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
