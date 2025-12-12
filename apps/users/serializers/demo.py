from typing import List

from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings

from ..roles import resolve_user_roles

User = get_user_model()


class DemoMeSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying user demo info.

    Includes expiration time and computed fields such as role and
    remaining time-to-live (TTL).
    """

    expires_at = serializers.DateTimeField(source="demo_expires_at", read_only=True)

    # Computed fields
    roles = serializers.SerializerMethodField()
    ttl_seconds_remaining = serializers.SerializerMethodField()
    ttl_hint = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "username",
            "is_demo",
            "expires_at",
            "roles",
            "ttl_seconds_remaining",
            "ttl_hint",
        )
        read_only_fields = fields

    def get_roles(self, obj) -> List[str]:
        return resolve_user_roles(obj)

    def get_ttl_seconds_remaining(self, obj) -> int | None:
        expires_at = getattr(obj, "demo_expires_at", None)
        if not expires_at:
            return None
        seconds = int((expires_at - timezone.now()).total_seconds())
        return max(seconds, 0)

    def get_ttl_hint(self, obj) -> str:
        # Return a human-friendly TTL
        secs = self.get_ttl_seconds_remaining(obj)
        if secs is None:
            return ""
        if secs <= 0:
            return "expired"
        mins = secs // 60
        if mins < 60:
            return f"~{mins}m left"
        hrs, rem = divmod(mins, 60)
        return f"~{hrs}h left" if rem == 0 else f"~{hrs}h {rem}m left"


class DemoSafeTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Validates a refresh token only if it belongs to an active demo user.

    Prevents expired demo users from obtaining a new access token during
    the token refresh process.
    """

    def validate(self, attrs):
        # Parse refresh to extract user id (no rotation yet).
        try:
            refresh = self.token_class(attrs["refresh"])
        except TokenError as e:
            raise InvalidToken(e.args[0])

        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM)
        if user_id is None:
            raise serializers.ValidationError({"detail": "Invalid token."})

        # Check demo status & expiry before rotating/issuing.
        now = timezone.now()
        is_valid_demo = User.objects.filter(
            **{
                api_settings.USER_ID_FIELD: user_id,
                "is_demo": True,
                "demo_expires_at__gt": now,
            }
        ).exists()

        if not is_valid_demo:
            raise serializers.ValidationError({"detail": "Demo session expired."})

        # Safe to rotate/issue tokens now.
        return super().validate(attrs)


class DemoLogoutSerializer(serializers.Serializer):
    """
    Payload for demo logout.
    """

    refresh = serializers.CharField(
        help_text="The SimpleJWT refresh token to blacklist.",
        trim_whitespace=True,
        allow_blank=False,
        write_only=True,
    )
