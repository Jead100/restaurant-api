from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes,
)

from apps.core.pagination import CustomPageNumberPagination
from apps.core.schema.responses import wrapped_response, SimpleDetailResponseSerializer
from apps.restaurant.mixins import DemoScopeMixin
from apps.users.permissions import IsManagerOrReadOnly

from ..filters import StrictOrderingFilter
from ..models import Category, MenuItem
from ..serializers.menu import (
    CategorySerializer,
    MenuItemResponseSerializer,
    MenuItemWriteSerializer,
)
from ..viewsets import RestaurantBaseViewSet


@extend_schema_view(
    list=extend_schema(
        summary="List all menu items",
        description="Returns a paginated list of menu items. "
        "Supports filtering (e.g., by price or category), "
        "searching by title, and ordering.",
        parameters=[
            OpenApiParameter(
                name="price__lte",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Maximum price to include in results",
            ),
            OpenApiParameter(
                name="featured",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Whether the item is featured (true or false).",
            ),
            OpenApiParameter(
                name="category",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by category ID.",
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single menu item",
        description="Returns detailed information about one menu item.",
        responses=wrapped_response(
            serializer_class=MenuItemResponseSerializer,
            detail_text=' message "Menu item retrieved successfully."',
            data_text="The menu item object.",
        ),
    ),
    create=extend_schema(
        summary="Create a new menu item",
        description="Adds a new item to the menu. Only users in the "
        "'Manager' group can perform this action.",
        responses=wrapped_response(
            serializer_class=MenuItemResponseSerializer,
            detail_text='message "Menu item created successfully."',
            data_text="The newly created menu item.",
        ),
    ),
    update=extend_schema(
        summary="Update a menu item",
        description="Replaces all fields of a menu item. "
        "Only accessible to managers.",
        responses=wrapped_response(MenuItemResponseSerializer),
    ),
    partial_update=extend_schema(
        summary="Partially update a menu item",
        description="Updates selected fields of a menu item. Managers only.",
        responses=wrapped_response(MenuItemResponseSerializer),
    ),
    destroy=extend_schema(
        summary="Delete a menu item",
        description="Removes a menu item from the system. Managers only.",
        responses={200: SimpleDetailResponseSerializer},
    ),
)
class MenuItemViewSet(DemoScopeMixin, RestaurantBaseViewSet):
    """
    Viewset for managing menu items.

    Supports listing, searching, filtering, creating, updating, and
    deleting menu items.

    Only authenticated users that belong to 'manager' group can
    perform write operations, enforced by `IsManagerOrReadOnly`.
    """

    queryset = MenuItem.objects.select_related("category").all()
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    # Read-only serializer used for list/retrieve responses and
    # for reserializing output in create/update actions
    res_serializer_cls = MenuItemResponseSerializer

    filter_backends = [DjangoFilterBackend, StrictOrderingFilter, filters.SearchFilter]
    filterset_fields = {
        "price": ["lte"],  # e.g., ?price__lte=10.0
        "featured": ["exact"],
        "category": ["exact"],
    }
    ordering_fields = ["id", "title", "price"]
    search_fields = ["title"]  # e.g., ?search=cake
    pagination_class = CustomPageNumberPagination

    # Used in default response messages via `self.msg()`
    resource_name = "Menu item"

    def get_serializer_class(self):
        """
        Returns the default serializer for an action in the viewset.
        """
        if self.action in ("create", "update", "partial_update"):
            return MenuItemWriteSerializer
        return self.res_serializer_cls


class CategoryViewSet(DemoScopeMixin, RestaurantBaseViewSet):
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
    lookup_field = "slug"
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    filter_backends = [DjangoFilterBackend, StrictOrderingFilter, filters.SearchFilter]
    ordering_fields = ["slug", "title"]
    search_fields = ["slug"]
    pagination_class = CustomPageNumberPagination

    resource_name = "Menu category"
    resource_plural_name = "Menu categories"
