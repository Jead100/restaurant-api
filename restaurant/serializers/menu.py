"""
Serializers for menu items and their categories.
"""

from rest_framework import serializers

from restaurant.models import MenuItem, Category


class MenuItemSerializer(serializers.HyperlinkedModelSerializer):
    """
    Menu item with price validation and hyperlinked `category`.
    """

    category = serializers.HyperlinkedRelatedField(
        view_name="category-detail", queryset=Category.objects.all()
    )

    class Meta:
        model = MenuItem
        fields = (
            "url",
            "id",
            "title",
            "price",
            "featured",
            "category",
        )
        read_only_fields = ("id",)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Must be a positive number.")
        if value > 100.0:
            raise serializers.ValidationError("Must not exceed 100.00.")
        return value


class MenuItemTinySerializer(serializers.ModelSerializer):
    """
    Minimal menu-item details (id + title as `name`).
    """

    name = serializers.CharField(source="title")

    class Meta:
        model = MenuItem
        fields = (
            "id",
            "name",
        )


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for menu categories (e.g., desserts, appetizers).
    """

    class Meta:
        model = Category
        fields = (
            "url",
            "id",
            "slug",
            "title",
        )
        read_only_fields = ("id",)
