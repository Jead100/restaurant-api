from rest_framework.permissions import (
    BasePermission, SAFE_METHODS
)


MANAGER_GROUP_NAME = "Manager"
DELIVERY_GROUP_NAME = "Delivery crew"


class IsManager(BasePermission):
    """
    Allows access only to users in the 'Manager' group.

    Assumes the user is already authenticated.
    """
    message = "You must be a manager to perform this action."

    def has_permission(self, request, view):
        # IsAuthenticated will run first, 
        # so we can rely on request.user existing.
        return (
            request.user.groups.filter(name=MANAGER_GROUP_NAME).exists()
        )


class IsDeliveryCrew(BasePermission):
    """
    Allows access only to users in the 'Delivery crew' group.

    Assumes the user is already authenticated.
    """
    message = "You must be a delivery crew member to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user.groups.filter(name=DELIVERY_GROUP_NAME).exists()
        )


class IsManagerOrDeliveryCrew(BasePermission):
    """
    Allows access only to users in the 'Manager' or
    'Delivery crew' group.

    Assumes the user is already authenticated.
    """
    message = "You must be a manager or delivery crew member " \
              "to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user.groups.filter(
                name__in=[MANAGER_GROUP_NAME, DELIVERY_GROUP_NAME]
            ).exists()
        )


class IsCustomer(BasePermission):
    """
    A customer is defined as a user that does not belong
    to the 'Manager' or 'Delivery Crew' group.
    """
    message = "You must be a customer to perform this action."

    def has_permission(self, request, view):
        return not (
            request.user.groups.filter(
                name__in=[MANAGER_GROUP_NAME, DELIVERY_GROUP_NAME]
            ).exists()
        )
        

class IsManagerOrReadOnly(BasePermission):
    """
    The request is from a user in the 'Manager' group, 
    or is a read-only request.
    """
    message = "You must be a manager to perform write actions."

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user.groups.filter(name=MANAGER_GROUP_NAME).exists()
        )
