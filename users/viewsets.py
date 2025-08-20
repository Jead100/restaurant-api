from django.contrib.auth.models import Group, User
from django.utils.functional import cached_property

from rest_framework import status

from core.mixins import model_mixins
from core.responses import format_response
from core.viewsets import ExtendedGenericViewSet

from users.serializers.groups import GroupUserSerializer, AddUserToGroupSerializer


class GroupMembershipViewSet(
    model_mixins.CustomListModelMixin,
    model_mixins.CustomCreateModelMixin,
    model_mixins.CustomRetrieveModelMixin,
    model_mixins.CustomDestroyModelMixin,
    ExtendedGenericViewSet,
):
    """
    List, add, retrieve, or remove users from a single Django group.

    Subclasses must set `group_name` (e.g., 'Delivery crew').
    """

    group_name = None  # must be overridden by subclasses

    @cached_property
    def group(self) -> Group:
        """
        Return the Django Group instance with name `group_name`.

        Cached per request.
        """
        return Group.objects.get(name=self.group_name)

    def get_queryset(self):
        """
        Return users in the group, ordered by ID.
        """
        return User.objects.filter(groups__name=self.group_name).order_by("id")

    def get_serializer_class(self):
        """
        Use `AddUserToGroupSerializer` for create;
        `GroupUserSerialzier` for all other actions.
        """
        if self.action == "create":
            return AddUserToGroupSerializer
        return GroupUserSerializer

    def create(self, request, *args, **kwargs):
        """
        Add user to the group if not already a member.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.context["user_instance"]

        if self.group.user_set.filter(id=user.id).exists():
            return format_response(
                detail=(
                    f"User '{user.username}' is already "
                    f"in the {self.group_name} group."
                ),
                data=None,
                status=status.HTTP_409_CONFLICT,
            )

        self.group.user_set.add(user)

        return format_response(
            detail=(
                f"User '{user.username}' successfully added"
                f"to the {self.group_name} group."
            ),
            data=None,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Remove user from the group.
        """
        user = self.get_object()
        self.group.user_set.remove(user)

        return format_response(
            detail=(
                f"User '{user.username}' successfully removed "
                f"from the {self.group_name} group."
            ),
            data=None,
            status=status.HTTP_200_OK,
        )
