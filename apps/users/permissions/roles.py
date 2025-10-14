from rest_framework.permissions import BasePermission, SAFE_METHODS

from ..roles import Role

STAFF_GROUPS = (Role.MANAGER.label, Role.DELIVERY_CREW.label)


class IsManager(BasePermission):
    """
    Allows access only to users in the 'Manager' group.

    Assumes the user is already authenticated.
    """

    message = "You must be a manager to perform this action."

    def has_permission(self, request, view):
        # IsAuthenticated will run first,
        # so we can rely on request.user existing.
        return request.user.groups.filter(name=Role.MANAGER.label).exists()


class IsDeliveryCrew(BasePermission):
    """
    Allows access only to users in the 'Delivery crew' group.

    Assumes the user is already authenticated.
    """

    message = "You must be a delivery crew member to perform this action."

    def has_permission(self, request, view):
        return request.user.groups.filter(name=Role.DELIVERY_CREW.label).exists()


class IsManagerOrDeliveryCrew(BasePermission):
    """
    Allows access only to users in the 'Manager' or
    'Delivery crew' group.

    Assumes the user is already authenticated.
    """

    message = "You must be a manager or delivery crew member to perform this action."

    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=STAFF_GROUPS).exists()


class IsCustomer(BasePermission):
    """
    A customer is defined as a user that does not belong
    to the 'Manager' or 'Delivery crew' group.
    """

    message = "You must be a customer to perform this action."

    def has_permission(self, request, view):
        return not (request.user.groups.filter(name__in=STAFF_GROUPS).exists())


class IsManagerOrReadOnly(BasePermission):
    """
    The request is from a user in the 'Manager' group,
    or is a read-only request.
    """

    message = "You must be a manager to perform write actions."

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.groups.filter(name=Role.MANAGER.label).exists()
        )
