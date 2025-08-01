from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """
    Menu item category (e.g., Appetizers, Desserts).
    """

    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)


class MenuItem(models.Model):
    """
    A food item offered on the menu.
    """

    title = models.CharField(max_length=255, unique=True, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)


class Cart(models.Model):
    """
    Temporary cart model for storing menu items added by a user
    before placing an order.

    `unit_price` should match the associated `menuitem` price.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        # Prevents duplicate menu items in the same user's cart
        constraints = [
            models.UniqueConstraint(
                fields=["user", "menuitem"], name="unique_user_menuitem"
            )
        ]


class Order(models.Model):
    """
    Represents a confirmed user/customer order.

    Delivery crew can be optionally assigned after creation.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True
    )
    # False = pending, True = completed
    status = models.BooleanField(db_index=True, default=False)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True)


class OrderItem(models.Model):
    """
    Line item in a user order, typically created from a cart item.

    All fields, but order, must mirror the corresponding cart item.
    """

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        # Prevents duplicate menu items in the same order
        constraints = [
            models.UniqueConstraint(
                fields=["order", "menuitem"], name="unique_order_menuitem"
            )
        ]
