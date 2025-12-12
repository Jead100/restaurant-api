from typing import List

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    """
    Defines the canonical user roles and their corresponding auth group labels.
    """

    # <ROLE> = "<slug>", "<group-name>"
    MANAGER = "manager", "Manager"
    DELIVERY_CREW = "delivery_crew", "Delivery crew"
    CUSTOMER = "customer", "Customer"  # note: customers don't need a group


# Collection of valid role slugs, e.g. ('manager', 'delivery_crew', 'customer')
ROLES = tuple(Role.values)


def resolve_user_roles(user: AbstractUser) -> List[str]:
    """
    Infer the user's roles from the auth groups they belong to
    and return them sorted by predefined priority.

    Users who do not belong to the 'Manager' or 'Delivery crew'
    group are considered customers.
    """

    try:
        group_names = set(user.groups.values_list("name", flat=True))
    except Exception:
        group_names = set()

    roles: List[str] = []

    if Role.MANAGER.label in group_names:
        roles.append(Role.MANAGER.value)
    if Role.DELIVERY_CREW.label in group_names:
        roles.append(Role.DELIVERY_CREW.value)

    # Default to "customer" if no specific role groups were found
    if not roles:
        roles.append(Role.CUSTOMER.value)

    # Enforce deterministic ordering
    priority = {
        Role.MANAGER.value: 1,
        Role.DELIVERY_CREW.value: 2,
        Role.CUSTOMER.value: 3,
    }
    roles.sort(key=lambda r: priority.get(r, 99))

    return roles
