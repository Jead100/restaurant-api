from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying minimal user info.
    """

    class Meta:
        model = User
        fields = ("id", "username")


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
