"""
Serializers for user data across Little Lemon API.
"""

from rest_framework import serializers

from ..models import User


class GroupUserSerializer(serializers.ModelSerializer):
    """
    Basic user details for group membership endpoints.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
        )
        read_only_fields = fields


class AddUserToGroupSerializer(serializers.Serializer):
    """
    Look up a user by username and stash the instance in `context`.
    """

    username = serializers.CharField()

    def validate_username(self, value):
        # Ensure the user exists
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User '{value}' does not exist.")

        # Cache the instance for the view
        self.context["user_instance"] = user

        return value
