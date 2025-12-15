from typing import List

from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..roles import resolve_user_roles

User = get_user_model()


class UserTinySerializer(serializers.ModelSerializer):
    """
    Serializer for minimal user info.
    """

    class Meta:
        model = User
        fields = ("id", "username")


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for basic user info with roles.
    """

    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "roles")

    def get_roles(self, obj) -> List[str]:
        return resolve_user_roles(obj)


class UsernameLookupSerializer(serializers.Serializer):
    """
    Serializer for validating a username exists.
    """

    username = serializers.CharField()

    def validate(self, attrs):
        username = attrs["username"]
        # Ensure user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User '{username}' does not exist.")

        # Attach user instance to validated_data for use in view
        attrs["user"] = user

        return attrs
