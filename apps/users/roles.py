from django.db import models


class Role(models.TextChoices):
    # <ROLE> = "<slug>", "<group-name>"
    MANAGER = "manager", "Manager"
    DELIVERY_CREW = "delivery_crew", "Delivery crew"
    CUSTOMER = "customer", "Customer"  # customers don't need a group


# Collection of valid role slugs
ROLES = tuple(Role.values)  # -> ('manager', 'delivery_crew', 'customer')


def get_user_role(user) -> str:
    """
    Return the role of a user based on *group* membership.

    A user that does not belong to the 'Manager' or
    'Delivery crew' group is considered a customer.
    """
    if user.groups.filter(name=Role.MANAGER.label).exists():
        return Role.MANAGER.value
    if user.groups.filter(name=Role.DELIVERY_CREW.label).exists():
        return Role.DELIVERY_CREW.value
    return Role.CUSTOMER.value
