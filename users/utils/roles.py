from django.contrib.auth.models import User


def get_user_role(user: User) -> str:
    """
    Return the role of a user based on group membership.

    Roles:
    - 'manager' if user is in 'Manager' group
    - 'delivery_crew' if user is in 'Delivery crew' group
    - 'customer' otherwise
    """
    if user.groups.filter(name="Manager").exists():
        return "manager"
    if user.groups.filter(name="Delivery crew").exists():
        return "delivery_crew"
    return "customer"
