"""
Serializers for menu items and their categories.
"""

from django.urls import reverse
from rest_framework import serializers
from ..models import MenuItem, Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for menu categories (e.g., desserts, appetizers).
    """

    links = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "title", "slug", "links")
        read_only_fields = ("id", "links")

    def get_links(self, obj):
        request = self.context.get("request")
        return {
            "self": request.build_absolute_uri(
                reverse("restaurant:category-detail", args=[obj.slug])
            )
        }


class CategoryTinySerializer(serializers.ModelSerializer):
    """
    Minimal category details (title + url)
    for embedding in menu item lines.
    """

    links = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("title", "links")
        read_only_fields = fields

    def get_links(self, obj):
        request = self.context.get("request")
        return {
            "self": request.build_absolute_uri(
                reverse("restaurant:category-detail", args=[obj.slug])
            )
        }


class MenuItemResponseSerializer(serializers.HyperlinkedModelSerializer):
    category = CategoryTinySerializer(read_only=True)
    links = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ("id", "title", "price", "featured", "category", "links")
        read_only_fields = fields

    def get_links(self, obj):
        request = self.context.get("request")
        return {
            "self": request.build_absolute_uri(
                reverse("restaurant:menuitem-detail", args=[obj.pk])
            )
        }


class MenuItemWriteSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        help_text="The ID of the category this item belongs to.",
    )

    class Meta:
        model = MenuItem
        fields = ("title", "price", "featured", "category")

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Must be a positive number.")
        if value > 100.0:
            raise serializers.ValidationError("Must not exceed 100.00.")
        return value


class MenuItemTinySerializer(serializers.ModelSerializer):
    """
    Minimal menu-item details (id + title as `name`)
    for embedding in cart lines.
    """

    name = serializers.CharField(source="title")

    class Meta:
        model = MenuItem
        fields = ("id", "name")
        read_only_fields = fields
