"""
Serializers for cart items (read, create, update).
"""

from rest_framework import serializers

from apps.core.serializers.mixins import StrictFieldsMixin

from ..models import MenuItem, Cart
from ..serializers.menu import MenuItemTinySerializer


class CartResponseSerializer(serializers.ModelSerializer):
    """
    Read-only cart item representation
    """

    menuitem = MenuItemTinySerializer(read_only=True)

    class Meta:
        model = Cart
        fields = (
            "id",
            "menuitem",
            "quantity",
            "unit_price",
            "price",
        )
        read_only_fields = fields


class CartCreateSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    """
    Create a cart line from `menuitem_id` and `quantity`.
    """

    menuitem_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(),
        source="menuitem",
    )
    quantity = serializers.IntegerField(min_value=1, max_value=99)

    class Meta:
        model = Cart
        fields = (
            "menuitem_id",
            "quantity",
        )

    def validate(self, attrs):
        # Check if a cart line with the user from the request context
        # and the menu item already exists.
        user = self.context["request"].user
        menuitem = attrs["menuitem"]
        if Cart.objects.filter(user=user, menuitem=menuitem).exists():
            raise serializers.ValidationError(
                {"menuitem_id": "This item is already in your cart."}
            )
        return attrs

    def create(self, validated_data):
        # Get user from the request context for creating the cart line
        user = self.context["request"].user
        menuitem = validated_data["menuitem"]
        qty = validated_data["quantity"]

        return Cart.objects.create(
            user=user,
            menuitem=menuitem,
            quantity=qty,
            unit_price=menuitem.price,
            price=menuitem.price * qty,
        )


class CartUpdateSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    """
    Update a cart line's quantity only.
    """

    quantity = serializers.IntegerField(min_value=1, max_value=99)

    class Meta:
        model = Cart
        fields = ("quantity",)

    def validate(self, attrs):
        # Require `quantity` even when the request was partial
        if self.partial and "quantity" not in attrs:
            raise serializers.ValidationError({"quantity": "This field is required."})
        return super().validate(attrs)

    def update(self, instance, validated_data):
        """
        Re-calculate `price` when quantity changes.
        """
        quantity = validated_data.get("quantity", instance.quantity)
        validated_data["price"] = instance.unit_price * quantity
        return super().update(instance, validated_data)
