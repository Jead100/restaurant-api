"""
Base viewset for all restaurant views.
"""

from core.mixins import model_mixins
from core.viewsets import ExtendedGenericViewSet


class RestaurantBaseViewSet(
    model_mixins.CustomCreateModelMixin,
    model_mixins.CustomRetrieveModelMixin,
    model_mixins.CustomUpdateModelMixin,
    model_mixins.CustomDestroyModelMixin,
    model_mixins.CustomListModelMixin,
    ExtendedGenericViewSet,
):
    """
    Provides all standard CRUD actions such as `create()`,
    `retrieve()`, `update()`, and `destroy()`, plus
    `partial_update()` and `list()` via `core.mixins.model_mixins'.
    """

    pass
