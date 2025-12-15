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
from apps.core.schemas import SimpleDetailSerializer
from apps.restaurant.mixins import RestaurantDemoGuardMixin
from apps.users.permissions import IsManagerOrReadOnly

from ..filters import StrictOrderingFilter
from ..models import Category, MenuItem
from ..serializers.menu import (
    CategorySerializer,
    MenuItemResponseSerializer,
    MenuItemWriteSerializer,
)
from ..viewsets import RestaurantBaseViewSet
from ..schemas import MenuItemEnvelopeSerializer, CategoryEnvelopeSerializer


@extend_schema(tags=["Menu"])
@extend_schema_view(
    list=extend_schema(
        summary="Retrieve a list of all menu items.",
        description=(
            "Returns a paginated list of menu items.\n\n"
            "Supports filtering by price, featured status, and category, "
            "as well as searching by title, and ordering results."
        ),
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
        summary="Retrieve a menu item by ID.",
        description=(
            "Returns detailed information for a single menu item "
            "identified by its ID."
        ),
        responses={200: MenuItemEnvelopeSerializer},
    ),
    create=extend_schema(
        summary="Create a new menu item.",
        description=(
            "Creates a new menu item.\n\n"
            "Only users in the 'Manager' group can perform this action."
        ),
        responses={201: MenuItemEnvelopeSerializer},
    ),
    update=extend_schema(
        summary="Replace a menu item with new data.",
        description=(
            "Replaces all fields of an existing menu item.\n\n"
            "Only users in the 'Manager' group can perform this action."
        ),
        responses={200: MenuItemEnvelopeSerializer},
    ),
    partial_update=extend_schema(
        summary="Partially update a menu item.",
        description=(
            "Updates one or more fields of an existing menu item.\n\n"
            "Only users in the 'Manager' group can perform this action."
        ),
        responses={200: MenuItemEnvelopeSerializer},
    ),
    destroy=extend_schema(
        summary="Delete a menu item.",
        description=(
            "Permanently removes a menu item.\n\n"
            "Only users in the 'Manager' group can perform this action."
        ),
        responses={200: SimpleDetailSerializer},
    ),
)
class MenuItemViewSet(RestaurantDemoGuardMixin, RestaurantBaseViewSet):
    """
    Viewset for managing menu items.

    Supports listing, searching, filtering, creating, updating, and
    deleting menu items.

    Only authenticated users in the 'Manager' group can perform
    write operations; all authenticated users can read menu items.
    """

    queryset = MenuItem.objects.select_related("category").all()
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    # Read-only serializer used for list/retrieve responses and
    # for reserializing output in create/update actions
    res_serializer_cls = MenuItemResponseSerializer

    filter_backends = [DjangoFilterBackend, StrictOrderingFilter, filters.SearchFilter]
    filterset_fields = {
        "price": ["lte"],
        "featured": ["exact"],
        "category": ["exact"],
    }
    ordering_fields = ["title", "price", "featured", "category__title"]
    search_fields = ["title", "category__title"]
    pagination_class = CustomPageNumberPagination

    # Used in default response messages via `self.msg()`
    resource_name = "Menu item"

    def get_serializer_class(self):
        # Use write serializer for write actions, read serializer otherwise.
        if self.action in ("create", "update", "partial_update"):
            return MenuItemWriteSerializer
        return self.res_serializer_cls


@extend_schema(tags=["Categories"])
@extend_schema_view(
    list=extend_schema(
        summary="Retrieve a list of all categories.",
        description=(
            "Returns a paginated list of menu categories.\n\n"
            "Supports searching by slug and ordering by `slug` or `title`."
        ),
    ),
    retrieve=extend_schema(
        summary="Retrieve a category by slug.",
        description=(
            "Returns detailed information for a single menu category "
            "identified by its slug."
        ),
        responses={200: CategoryEnvelopeSerializer},
    ),
    create=extend_schema(
        summary="Create a new category.",
        description=(
            "Creates a new menu category.\n\n"
            "Only users in the 'Manager' group can perform this action."
        ),
        responses={201: CategoryEnvelopeSerializer},
    ),
    update=extend_schema(
        summary="Replace a category with new data.",
        description=(
            "Replaces all fields of an existing menu category.\n\n"
            "Only users in the 'Manager' group can perform this action."
        ),
        responses={200: CategoryEnvelopeSerializer},
    ),
    partial_update=extend_schema(
        summary="Partially update a category.",
        description=(
            "Updates one or more fields of an existing menu category.\n\n"
            "Only users in the 'Manager' group can perform this action."
        ),
        responses={200: CategoryEnvelopeSerializer},
    ),
    destroy=extend_schema(
        summary="Delete a category.",
        description=(
            "Permanently removes a menu category.\n\n"
            "Only users in the 'Manager' group can perform this action."
        ),
        responses={200: SimpleDetailSerializer},
    ),
)
class CategoryViewSet(RestaurantDemoGuardMixin, RestaurantBaseViewSet):
    """
    Viewset for managing menu item categories.

    Supports listing, searching, and ordering of categories, as well as
    creation, updating, and deletion

    Only authenticated users in the 'Manager' group can perform
    write operations; all authenticated users can read categories.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]
    lookup_field = "slug"
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    filter_backends = [DjangoFilterBackend, StrictOrderingFilter, filters.SearchFilter]
    ordering_fields = ["slug", "title"]
    search_fields = ["slug", "title"]
    pagination_class = CustomPageNumberPagination

    resource_name = "Menu category"
    resource_plural_name = "Menu categories"
