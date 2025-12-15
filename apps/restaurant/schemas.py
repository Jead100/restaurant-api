from drf_spectacular.utils import extend_schema_serializer

from apps.core.schemas import BaseEnvelopeSerializer
from .serializers import (
    CategorySerializer,
    MenuItemResponseSerializer,
    CartResponseSerializer,
    OrderResponseSerializer,
)


@extend_schema_serializer(component_name="CategoryEnvelope")
class CategoryEnvelopeSerializer(BaseEnvelopeSerializer):
    """
    Envelope schema for category objects
    """

    data = CategorySerializer(
        help_text="Category resource.",
        read_only=True,
    )


@extend_schema_serializer(component_name="MenuItemEnvelope")
class MenuItemEnvelopeSerializer(BaseEnvelopeSerializer):
    """
    Envelope schema for menu item objects
    """

    data = MenuItemResponseSerializer(
        help_text="Menu item resource.",
        read_only=True,
    )


@extend_schema_serializer(component_name="CartItemEnvelope")
class CartItemEnvelopeSerializer(BaseEnvelopeSerializer):
    """
    Envelope schema for cart line objects
    """

    data = CartResponseSerializer(
        help_text="Cart item resource.",
        read_only=True,
    )


@extend_schema_serializer(component_name="OrderEnvelope")
class OrderEnvelopeSerializer(BaseEnvelopeSerializer):
    """
    Envelope schema for order objects
    """

    data = OrderResponseSerializer(
        help_text="Order resource",
        read_only=True,
    )
