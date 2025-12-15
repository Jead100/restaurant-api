from django.utils.translation import gettext_lazy as _

from rest_framework import filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from apps.core.pagination import CustomPageNumberPagination
from apps.core.responses import format_response
from apps.restaurant.mixins import RestaurantDemoGuardMixin
from apps.users.permissions import IsCustomer

from ..filters import StrictOrderingFilter
from ..models import Cart
from ..serializers.cart import (
    CartCreateSerializer,
    CartResponseSerializer,
    CartUpdateSerializer,
)
from ..viewsets import RestaurantBaseViewSet


class CartViewSet(RestaurantDemoGuardMixin, RestaurantBaseViewSet):
    """
    Viewset for managing a user's cart.

    Customers can list, add, update, or remove individual items from their
    cart, and can also clear the entire cart.

    Each cart is user-specific and scoped to the authenticated customer,
    enforced by `IsCustomer` permission.
    """

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
