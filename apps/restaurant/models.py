from django.conf import settings
from django.db import models
from django.db.models import Q


class DemoTrackedModel(models.Model):
    """
    Abstract base model that adds demo-sandbox tracking
    for the concrete restaurant models.

    `is_demo` can be used to scope write operations (e.g., only
    allow public writes on demo rows) and to prune demo data.
    """

    is_demo = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Indicates whether this row was created in demo mode.",
    )

    class Meta:
        abstract = True


class Category(DemoTrackedModel):
    """
    Menu item category (e.g., Appetizers, Desserts).
    """

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["title"]

    def __str__(self):
        return self.title


class MenuItem(DemoTrackedModel):
    """
    A food item offered on the menu.
    """

    title = models.CharField(
        max_length=255,
        unique=True,
        help_text="The name of the menu item.",
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        db_index=True,
        help_text="The price of the item in USD.",
    )
    featured = models.BooleanField(
        db_index=True, help_text="Indicates whether the item is featured."
    )
    category = models.ForeignKey(
        to=Category,
        on_delete=models.PROTECT,
        related_name="items",
        help_text="The category this item belongs to.",
    )

    class Meta:
        verbose_name_plural = "menu items"
        ordering = ["-featured", "title"]

    def __str__(self):
        return f"{self.title} ({self.category.title})"


class Cart(DemoTrackedModel):
    """
    Temporary cart model for storing menu items added by a user
    before placing an order.

    `unit_price` should match the associated `menuitem` price.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
        indexes = [models.Index(fields=["user", "menuitem"])]


class Order(DemoTrackedModel):
    """
    Represents a confirmed user/customer order.

    Delivery crew can be optionally assigned after creation.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="delivery_crew",
        null=True,
    )
    status = models.BooleanField(
        db_index=True, default=False
    )  # False = pending, True = completed
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True)

    class Meta:
        ordering = ["-date", "-id"]


class OrderItem(models.Model):
    """
    Line item in a user order, typically created from a cart item.

    All fields, but order, must mirror the corresponding cart item.
    """

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    menuitem = models.ForeignKey(
        MenuItem, on_delete=models.SET_NULL, null=True, blank=True
    )
    item_title = models.CharField(max_length=255)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        # Prevents duplicate menu items in the same order
        constraints = [
            models.UniqueConstraint(
                fields=["order", "menuitem"],
                condition=Q(menuitem__isnull=False),
                name="uniq_order_menuitem_when_present",
            )
        ]
