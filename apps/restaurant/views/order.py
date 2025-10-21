from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from apps.core.pagination import CustomPageNumberPagination
from apps.core.responses import format_response
from apps.restaurant.mixins import RestaurantDemoGuardMixin
from apps.users.permissions import IsCustomer, IsManager, IsManagerOrDeliveryCrew
from apps.users.roles import get_user_role


from ..filters import OrderFilter, StrictOrderingFilter
from ..models import Cart, Order, OrderItem
from ..serializers.order import (
    DeliveryCrewOrderUpdateSerializer,
    ManagerOrderResponseSerializer,
    ManagerOrderUpdateSerializer,
    OrderResponseSerializer,
)
from ..viewsets import RestaurantBaseViewSet


class OrderViewSet(RestaurantDemoGuardMixin, RestaurantBaseViewSet):
    """
    Viewset for managing customer orders.

    Supports listing, retrieving, creating, and updating orders
    based on user role, enforced by `HasPermissionToOrderAction`.

    Managers can view and update all orders, assign delivery crew,
    and change order statuses. Delivery crew can view and update their
    assigned orders. Customers can view and create their own orders.
    """

    # Default base permission
    permission_classes = (IsAuthenticated,)

    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, StrictOrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ["id", "date", "status", "total"]
    ordering = ["-date"]  # default ordering
    pagination_class = CustomPageNumberPagination

    resource_name = "Order"

    READ_SERIALIZERS = {
        "manager": ManagerOrderResponseSerializer,
        "delivery_crew": OrderResponseSerializer,
        "customer": OrderResponseSerializer,
    }
    WRITE_SERIALIZERS = {
        "manager": ManagerOrderUpdateSerializer,
        "delivery_crew": DeliveryCrewOrderUpdateSerializer,
    }

    @cached_property
    def user_role(self):
        return get_user_role(self.request.user)

    @property
    def res_serializer_cls(self):
        # Role-specific read-only serializer for response
        # reserialization in create/update actions
        return self.READ_SERIALIZERS[self.user_role]

    @property
    def default_messages(self):
        # Override the 'list' message template in `self.default_messages`
        # for dynamic, role-specific output
        messages = super().default_messages.copy()
        messages["list"] = _("{list_scope}")
        return messages

    def get_permissions(self):
        permission_list = list(self.permission_classes)
        method = self.request.method
        if method == "POST":
            # Only customers can POST orders
            permission_list += [IsCustomer]
        elif method in ("PUT", "PATCH"):
            # Only managers or delivery crew can update orders
            permission_list += [IsManagerOrDeliveryCrew]
        elif method == "DELETE":
            # Only managers can DELETE orders
            permission_list += [IsManager]

        self.permission_classes = permission_list
        return super().get_permissions()

    def get_msg_context(self):
        # Add role-based context for dynamic 'list' message
        # rendered via self.msg('list')
        context = super().get_msg_context()

        if self.user_role == "delivery_crew":
            context["list_scope"] = (
                f"Orders assigned to delivery crew '{self.request.user.username}'."
            )
        elif self.user_role == "customer":
            context["list_scope"] = f"Orders for user '{self.request.user.username}'."
        else:
            context["list_scope"] = "Orders"

        return context

    def get_queryset(self):
        # Return a filtered queryset based on the user's role.
        # Managers see all orders, delivery crew see assigned orders,
        # and customers see only their own orders.
        qs = Order.objects.all().prefetch_related("order_items__menuitem")

        if self.user_role == "manager":
            return qs.select_related("user", "delivery_crew")
        elif self.user_role == "delivery_crew":
            return qs.filter(delivery_crew=self.request.user)
        elif self.user_role == "customer":
            return qs.filter(user=self.request.user)
        return Order.objects.none()

    def get_serializer_class(self):
        # Return the appropriate serializer based on action and user role.
        # Write serializers are used for updates; read serializers for
        # all other actions.
        if self.action in ("update", "partial_update"):
            return self.WRITE_SERIALIZERS.get(self.user_role, OrderResponseSerializer)

        return self.READ_SERIALIZERS[self.user_role]

    def create(self, request, *args, **kwargs):
        """
        Create an order from the user's cart.

        Overrides the default to ensure the cart is not empty,
        we generate order items from cart items, and clear the cart
        after creation.
        """
        user = request.user
        cart_items = Cart.objects.filter(user=user).select_related("menuitem")
        if not cart_items.exists():
            return format_response(
                detail=(
                    "Your cart is empty. "
                    "Add items to your cart before placing an order."
                ),
                data=None,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create an order; delivery_crew remains unassigned
        order = Order.objects.create(
            user=user,
            total=0,  # will be updated after calculating item totals
            date=timezone.now().date(),
        )

        # Use DemoScopeMixin helper _is_demo_mode_enabled() to
        # check if the order was created in a demo sandbox
        if self._is_demo_mode_enabled:
            order.is_demo = True

        # Prepare order items and calculate order total
        total_order_price = 0
        order_items_to_create = []
        for cart_item in cart_items:
            order_item = OrderItem(
                order=order,
                menuitem=cart_item.menuitem,
                item_title=cart_item.menuitem.title,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price,
            )
            order_items_to_create.append(order_item)
            total_order_price += cart_item.price

        # Bulk create all order items for efficiency
        OrderItem.objects.bulk_create(order_items_to_create)

        # Update the order total and save
        order.total = total_order_price
        order.save()

        # Clear user's cart after successful order creation
        cart_items.delete()

        # Return the created order
        res_serializer = self.res_serializer_cls(order)
        return format_response(
            detail=self.msg("create"),
            data=res_serializer.data,
            status=status.HTTP_201_CREATED,
        )
