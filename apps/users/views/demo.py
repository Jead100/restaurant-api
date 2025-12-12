import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView

from ..permissions.demo import IsActiveDemo
from ..roles import Role, ROLES
from ..serializers.demo import (
    DemoMeSerializer,
    DemoSafeTokenRefreshSerializer,
    DemoLogoutSerializer,
)


class DemoLoginView(APIView):
    """
    Creates a temporary demo user assigned to the requested role and
    returns JWT (access, refresh). User auto-expires after DEMO_USER_TTL_HOURS.
    """

    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if not getattr(settings, "DEMO_MODE", False):
            return Response(
                {"detail": "Demo mode is disabled."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Normalize and validate request input
        role_input = kwargs.get("role", "").strip().lower().replace("-", "_")
        try:
            role_enum = Role(role_input)
        except ValueError:
            return Response(
                {"detail": f"Invalid role. Use role={'|'.join(ROLES)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create user with a unique username
        random_suffix = secrets.token_urlsafe(8)[:9].lower()  # URL-safe-ish short ID
        username = f"demo_{random_suffix}"
        password = secrets.token_urlsafe(16)
        User = get_user_model()
        user = User.objects.create_user(
            username=username, password=password, email=f"{username}@demo-invalid.com"
        )

        ttl_hours = int(getattr(settings, "DEMO_USER_TTL_HOURS", 12))
        demo_expires_at = timezone.now() + timedelta(hours=ttl_hours)

        # Mark user as demo + set expiry
        if hasattr(user, "is_demo"):
            user.is_demo = True
        if hasattr(user, "demo_expires_at"):
            user.demo_expires_at = demo_expires_at
        user.save(update_fields=["is_demo", "demo_expires_at"] or None)

        # Assign group if not a customer (customers don't belong to one)
        if role_enum != Role.CUSTOMER:
            group, _ = Group.objects.get_or_create(
                name=role_enum.label
            )  # "Manager" / "Delivery crew"
            user.groups.add(group)

        role = role_enum.value  # 'manager' | 'delivery_crew' | 'customer'

        # Issue JWTs with demo-specific lifetime caps
        refresh = RefreshToken.for_user(user)

        DEMO_REFRESH_MAX = timedelta(hours=1)
        DEMO_ACCESS_MAX = timedelta(minutes=15)
        remaining = (demo_expires_at - timezone.now()).total_seconds()

        # Ensure tokens never outlive the demo account or their respective caps
        refresh.set_exp(lifetime=min(DEMO_REFRESH_MAX, timedelta(seconds=remaining)))
        access = refresh.access_token
        access.set_exp(lifetime=min(DEMO_ACCESS_MAX, timedelta(seconds=remaining)))

        data = {
            "detail": f"Temporary '{role}' account created. Expires in {ttl_hours}h.",
            "user": {
                "username": username,
                "role": role,
                "expires_at": demo_expires_at.isoformat(),
            },
            "auth": {
                "refresh": str(refresh),
                "access": str(access),
            },
        }
        return Response(data, status=status.HTTP_201_CREATED)


class DemoMeView(APIView):
    """
    Returns the authenticated demo user's profile and TTL information.
    """

    permission_classes = [IsAuthenticated, IsActiveDemo]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = DemoMeSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DemoTokenRefreshView(TokenRefreshView):
    """
    Takes a refresh token and returns an access type JSON web
    token if the refresh token is valid and the demo user
    hasn't expired.
    """

    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = DemoSafeTokenRefreshSerializer


class DemoLogoutView(APIView):
    """
    Takes a refresh token and blacklists it.  Used with the
    `rest_framework_simplejwt.token_blacklist` app installed.
    """

    permission_classes = [IsAuthenticated, IsActiveDemo]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = DemoLogoutSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            raise ValidationError({"refresh": "Invalid or expired token."})

        return Response(
            {"detail": "Demo user logged out."},
            status=status.HTTP_200_OK,
        )
