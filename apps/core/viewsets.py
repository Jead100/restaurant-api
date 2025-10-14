"""
A core building block for base viewsets like
`RestaurantBaseViewSet` and `GroupMembershipViewSet`
in the 'restaurant' and 'users' apps.
"""

from rest_framework.viewsets import GenericViewSet

from .mixins.message import ResponseMessageMixin


class ExtendedGenericViewSet(GenericViewSet, ResponseMessageMixin):
    """
    Extends DRF's `GenericViewSet` with support for
    resource naming and custom response messages.
    """

    pass
