"""
Read and update serializers for orders
"""

from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.serializers.mixins import StrictFieldsMixin

from restaurant.models import Order, OrderItem
from restaurant.serializers.menu import MenuItemTinySerializer


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
            "quantity",
            "unit_price",
            "price",
        )


class OrderReadSerializer(serializers.ModelSerializer):
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


class OrderUserSerializer(serializers.ModelSerializer):
    """
    Minimal user details for embedding in orders.
    """

    class Meta:
        model = User
        fields = ("id", "username")


class ManagerOrderReadSerializer(OrderReadSerializer):
    """
    Adds user and delivery-crew details for manager views.
    """

    user = OrderUserSerializer(read_only=True)
    delivery_crew = OrderUserSerializer(read_only=True)

    class Meta(OrderReadSerializer.Meta):
        fields = OrderReadSerializer.Meta.fields + ("user", "delivery_crew")


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


DELIVERY_GROUP_NAME = "Delivery crew"  # reused by queries & validation


def delivery_crew_only(value: User):
    """
    Ensure the given user belongs to the 'Delivery crew' group.
    """

    if value is None:  # allow clearing the courier
        return value

    if not value.groups.filter(name=DELIVERY_GROUP_NAME).exists():
        raise ValidationError(
            f'Invalid pk "{value.pk}" - user is not part of the Delivery crew group.'
        )
    return value


class ManagerOrderUpdateSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    """
    Managers may toggle `status` or change / clear the courier.
    """

    status = serializers.BooleanField(required=False)
    delivery_crew = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name=DELIVERY_GROUP_NAME),
        required=False,
        allow_null=True,
        validators=[delivery_crew_only],
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
