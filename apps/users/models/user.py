import uuid
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from .demo_mixins import DemoUserMixin, DemoUserQuerySet


class CustomUserManager(UserManager.from_queryset(DemoUserQuerySet)):
    """
    Extends Django's built-in UserManager to include demo-related queryset helpers.
    """

    pass


class User(DemoUserMixin, AbstractUser):
    """
    Custom user model that includes demo account fields and a UUID identifier.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.username
