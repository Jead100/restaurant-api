"""
API views for restaurant endpoints.

Defines viewsets for managing menu items, categories, 
carts, and orders, built on top of `RestaurantBaseViewSet` 
and Django REST Framework features like authentication, 
permissions, throttling, filtering, pagination, and 
serialization.
"""

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from core.pagination import CustomPageNumberPagination

from restaurant.filters import StrictOrderingFilter
from restaurant.models import Category, MenuItem
from restaurant.serializers.menu import (
    CategorySerializer, 
    MenuItemSerializer,
)
from restaurant.viewsets import RestaurantBaseViewSet

from users.permissions import IsManagerOrReadOnly


class MenuItemViewSet(RestaurantBaseViewSet):
    """
    Viewset for managing menu items.

    Supports listing, searching, filtering, creating, updating, and
    deleting menu items.

    Only authenticated users that are part of the 'Manager'group can
    perform write operations, enforced by `HasPermissionToMenuAction`.
    """

    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    filter_backends = [DjangoFilterBackend, StrictOrderingFilter, filters.SearchFilter]
    filterset_fields = {
        "price": ["lte"],  # e.g., ?price__lte=10.0
        "featured": ["exact"],
        "category": ["exact"],
    }
    ordering_fields = ["title", "price"]
    search_fields = ["title"]  # e.g., ?search=cake
    pagination_class = CustomPageNumberPagination

    # Used in default response messages via `self.msg()`
    resource_name = "Menu item"


class CategoryViewSet(RestaurantBaseViewSet):
    """
    Viewset for managing menu item categories.

    Supports listing, searching, and ordering of categories, as well as
    creation, updating, and deletion

    Only authenticated users that are part of the 'Manager' group can
    perform write operations, enforced by `HasPermissionToCategoryAction`.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]
    lookup_field = "pk"
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    filter_backends = [DjangoFilterBackend, StrictOrderingFilter, filters.SearchFilter]
    ordering_fields = ["slug", "title"]
    search_fields = ["slug"]
    pagination_class = CustomPageNumberPagination

    resource_name = "Menu category"
    resource_plural_name = "Menu categories"
