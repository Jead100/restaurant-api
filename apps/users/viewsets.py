from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property

from rest_framework import status

from apps.core.mixins import model_mixins
from apps.core.responses import format_response
from apps.core.viewsets import ExtendedGenericViewSet

from .serializers.users import UserSerializer, UsernameLookupSerializer

User = get_user_model()


class GroupMembershipViewSet(
    model_mixins.CustomListModelMixin,
    model_mixins.CustomRetrieveModelMixin,
    ExtendedGenericViewSet,
):
    """
    List, add, retrieve, or remove users from a single Django group.

    Subclasses must set `group_name` (e.g., 'Delivery crew').
    """

    group_name: str | None = None  # must be overridden by subclasses

    @cached_property
    def group(self) -> Group:
        """
        Return the Group instance for self.group_name, or raise if missing.
        """
        if not self.group_name:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must define `group_name`."
            )

        try:
            return Group.objects.get(name=self.group_name)
        except Group.DoesNotExist:
            raise ImproperlyConfigured(
                f"Required group '{self.group_name}' does not exist. "
                f"Create it via migration or admin panel."
            )

    def initial(self, request, *args, **kwargs):
        """
        Runs DRF's auth/perm/throttle plus group validation.
        """
        super().initial(request, *args, **kwargs)

        # Skip group validation for unmapped methods (will return normal 405),
        # and for meta methods like OPTIONS/HEAD
        if self.action is None or request.method in ("OPTIONS", "HEAD"):
            return

        # Validate & cache the group
        _ = self.group

    def get_queryset(self):
        """
        Return users in the group, ordered by ID.
        """
        return User.objects.filter(groups__id=self.group.id).order_by("id").distinct()

    def get_serializer_class(self):
        """
        Use `UsernameLookupSerializer` for create;
        `UserSerializer` for all other actions.
        """
        if self.action == "create":
            return UsernameLookupSerializer
        return UserSerializer

    def perform_create(self, serializer):
        # Add the validated user to the group
        user = serializer.validated_data["user"]
        self.group.user_set.add(user)

    def perform_destroy(self, instance):
        # Remove the specified user instance from the group
        self.group.user_set.remove(instance)

    def create(self, request, *args, **kwargs):
        """
        Add user to the group if not already a member.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        if self.group.user_set.filter(id=user.id).exists():
            return format_response(
                detail=(
                    f"User '{user.username}' is already "
                    f"in the {self.group.name} group."
                ),
                data=None,
                status=status.HTTP_409_CONFLICT,
            )

        self.perform_create(serializer)

        return format_response(
            detail=(
                f"User '{user.username}' successfully added "
                f"to the {self.group.name} group."
            ),
            data=None,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Remove user from the group.
        """
        user = self.get_object()
        self.perform_destroy(user)

        return format_response(
            detail=(
                f"User '{user.username}' successfully removed "
                f"from the {self.group.name} group."
            ),
            data=None,
            status=status.HTTP_200_OK,
        )
