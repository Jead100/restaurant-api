from django.utils.translation import gettext_lazy as _

from rest_framework import filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)

from apps.core.pagination import CustomPageNumberPagination
from apps.core.responses import format_response
from apps.core.schemas import SimpleDetailSerializer
from apps.restaurant.mixins import RestaurantDemoGuardMixin
from apps.restaurant.schemas import CartItemEnvelopeSerializer
from apps.users.permissions import IsCustomer

from ..filters import StrictOrderingFilter
from ..models import Cart
from ..serializers.cart import (
    CartCreateSerializer,
    CartResponseSerializer,
    CartUpdateSerializer,
)
from ..viewsets import RestaurantBaseViewSet


@extend_schema(tags=["Cart"])
@extend_schema_view(
    list=extend_schema(
        summary="Retrieve a list of all cart items.",
        description=(
            "Returns a paginated list of cart items belonging to the "
            "authenticated customer.\n\n"
            "Supports searching by menu item title and ordering by `price` or `id`."
        ),
    ),
    retrieve=extend_schema(
        summary="Retrieve a cart item by ID.",
        description=(
            "Returns detailed information for a single cart item belonging "
            "to the authenticated customer."
        ),
        responses={200: CartItemEnvelopeSerializer},
    ),
    create=extend_schema(
        summary="Add a new item to the cart.",
        description=(
            "Creates a new cart item for the authenticated customer.\n\n"
            "Only authenticated customers can perform this action."
        ),
        responses={201: CartItemEnvelopeSerializer},
    ),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(
        summary="Partially update a cart item.",
        description=(
            "Updates one or more fields of an existing cart item.\n\n"
            "Only authenticated customers can perform this action."
        ),
        responses={200: CartItemEnvelopeSerializer},
    ),
    destroy=extend_schema(
        summary="Delete a cart item.",
        description=(
            "Permanently removes a cart item from the authenticated "
            "customer's cart.\n\n"
            "Only authenticated customers can perform this action."
        ),
        responses={200: SimpleDetailSerializer},
    ),
)
class CartViewSet(RestaurantDemoGuardMixin, RestaurantBaseViewSet):
    """
    Viewset for managing a user's cart.

    Customers can list, add, update, or remove individual items from their
    cart, and can also clear the entire cart.

    Each cart is user-specific and scoped to the authenticated customer,
    enforced by `IsCustomer` permission.
    """

    # Base queryset; for schema/model introspection
    queryset = Cart.objects.all()

    permission_classes = [IsAuthenticated, IsCustomer]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    filter_backends = [StrictOrderingFilter, filters.SearchFilter]
    search_fields = ["menuitem__title"]
    ordering_fields = ["price", "id"]
    ordering = ["id"]
    pagination_class = CustomPageNumberPagination

    # Read-only serializer used for list/retrieve responses and
    # for reserializing output in create/update actions
    res_serializer_cls = CartResponseSerializer

    # Action-specific success message templates (used by self.msg())
    default_messages = {
        "list": _("{resource_plural} in the cart for user '{username}'."),
        "create": _("{resource} added to cart successfully."),
        "retrieve": _("{resource} details"),
        "update": _("{resource} updated successfully."),
        "destroy": _("{resource} removed from cart successfully."),
    }

    def get_queryset(self):
        # Return cart items for the authenticated user
        return Cart.objects.filter(user=self.request.user).select_related("menuitem")

    def get_serializer_class(self):
        # Return the write serializer for create/update actions,
        # otherwise use the read-only serializer.
        if self.action == "create":
            return CartCreateSerializer
        if self.action in ("update", "partial_update"):
            return CartUpdateSerializer
        return self.res_serializer_cls

    def get_msg_context(self):
        # Extend message context with username, used in the 'list' message
        # rendered by self.msg("list") in the list action
        context = super().get_msg_context()
        context["username"] = self.request.user.username
        return context

    @extend_schema(
        summary="Clear all items from the cart.",
        description=(
            "Deletes all items from the authenticated customer's cart.\n\n"
            "Only authenticated customers can perform this action."
        ),
        responses={200: SimpleDetailSerializer},
    )
    @action(detail=False, methods=["delete"], url_path="clear", url_name="clear-cart")
    def clear_cart(self, request, *args, **kwargs):
        """
        Delete all items from the authenticated user's cart.
        """
        cart = Cart.objects.filter(user=request.user)
        if not cart.exists():
            return format_response(
                detail="No items in cart. Nothing to clear.",
                data=None,
                status=status.HTTP_200_OK,
            )

        cart.delete()
        return format_response(
            detail="Cart cleared successfully.", data=None, status=status.HTTP_200_OK
        )
