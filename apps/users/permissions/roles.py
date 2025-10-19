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


class IsCustomer(BasePermission):
    """
    A customer is defined as a user that does not belong
    to the 'Manager' or 'Delivery crew' group.
    """

    message = "You must be a customer to perform this action."

    def has_permission(self, request, view):
        return not (request.user.groups.filter(name__in=STAFF_GROUPS).exists())


class IsManagerOrDeliveryCrew(BasePermission):
    """
    Allows access only to users in the 'Manager' or
    'Delivery crew' group.

    Assumes the user is already authenticated.
    """

    message = "You must be a manager or delivery crew member to perform this action."

    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=STAFF_GROUPS).exists()


class IsManagerOrAdminUser(BasePermission):
    """
    Allows access only to users in the 'Manager' group or
    admin users (is_staff or is_superuser).
    """

    message = "You must be a manager or an admin user to perform this action."

    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name=Role.MANAGER.label).exists()
        )


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


class IsManagerForReadOnlyOrAdminUser(BasePermission):
    """
    The request is from a user in the 'Manager' group for read-only access,
    or from an admin user for full access.
    """

    message = "You must be a manager to perform read-only actions, \
                or an admin user to perform all actions."

    def has_permission(self, request, view):
        user = request.user
        admin_user = user.is_staff or user.is_superuser

        # Read access
        if request.method in SAFE_METHODS:
            if admin_user or user.groups.filter(name=Role.MANAGER.label).exists():
                return True
            else:
                self.message = (
                    "You must be an admin user or a manager to perform this action."
                )
                return False

        # Write access
        if admin_user:
            return True

        self.message = "You must be an admin user to perform this action."
        return False
