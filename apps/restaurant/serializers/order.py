"""
Read and update serializers for orders
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.core.serializers.mixins import StrictFieldsMixin
from apps.users.roles import Role
from apps.users.serializers import UserTinySerializer

from ..models import Order, OrderItem
from ..serializers.menu import MenuItemTinySerializer

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the individual items in an order.
    """

    menuitem = MenuItemTinySerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "menuitem",
            "item_title",
            "unit_price",
            "quantity",
            "price",
        )


class OrderResponseSerializer(serializers.ModelSerializer):
    """
    Base serializer for viewing a single order or order list.
    """

    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "date",
            "status",
            "total",
            "order_items",
        )
        read_only_fields = fields


class ManagerOrderResponseSerializer(OrderResponseSerializer):
    """
    Adds user and delivery-crew details for manager views.
    """

    user = UserTinySerializer(read_only=True)
    delivery_crew = UserTinySerializer(read_only=True)

    class Meta(OrderResponseSerializer.Meta):
        fields = OrderResponseSerializer.Meta.fields + ("user", "delivery_crew")


class DeliveryCrewOrderUpdateSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    """
    Delivery crew can update only the order's `status` flag.
    """

    status = serializers.BooleanField()

    class Meta:
        model = Order
        fields = ("status",)

    def validate(self, attrs):
        # Force `status` to be provided even on PATCH
        if self.partial and "status" not in attrs:
            raise serializers.ValidationError({"status": "This field is required."})
        return super().validate(attrs)


class ManagerOrderUpdateSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    """
    Managers may toggle `status` or change / clear the courier.
    """

    status = serializers.BooleanField(required=False)
    delivery_crew = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name=Role.DELIVERY_CREW.label),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Order
        fields = ("status", "delivery_crew")

    def validate(self, attrs):
        # Require at least one of `status` or `delivery_crew`
        if not attrs:
            raise serializers.ValidationError(
                "Provide at least one of 'status' or 'delivery_crew'."
            )
        return super().validate(attrs)
