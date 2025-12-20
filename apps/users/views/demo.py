import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils import timezone

from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView

from drf_spectacular.utils import extend_schema, inline_serializer

from apps.core.schemas import SimpleDetailSerializer

from ..permissions.demo import IsActiveDemo
from ..roles import Role, ROLES
from ..serializers.demo import (
    DemoMeSerializer,
    DemoSafeTokenRefreshSerializer,
    DemoLogoutSerializer,
)

User = get_user_model()


@extend_schema(
    tags=["Demo Authentication"],
    summary="Create a demo user and issue tokens.",
    description=(
        "Creates a temporary demo user for the requested role and returns "
        "an access and refresh JSON web token pair.\n\n"
        "The demo user automatically expires after the configured "
        "`DEMO_USER_TTL_HOURS` (you can see the exact expiry time in the response)."
    ),
    request=None,
    responses={
        201: inline_serializer(
            name="DemoLoginResponse",
            fields={
                "detail": serializers.CharField(),
                "user": inline_serializer(
                    name="DemoLoginUser",
                    fields={
                        "username": serializers.CharField(),
                        "role": serializers.CharField(),
                        "expires_at": serializers.DateTimeField(),
                    },
                ),
                "auth": inline_serializer(
                    name="DemoLoginTokens",
                    fields={
                        "refresh": serializers.CharField(),
                        "access": serializers.CharField(),
                    },
                ),
            },
        )
    },
)
class DemoLoginView(APIView):
    """
    Creates a temporary demo user assigned to the requested role
    and returns an access and refresh JSON web token pair.

    User auto-expires after DEMO_USER_TTL_HOURS.
    """

    permission_classes = [AllowAny]
    throttle_scope = "demo_create"

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

        with transaction.atomic():
            # Create user with a unique username
            random_suffix = secrets.token_urlsafe(8)[:9].lower()
            username = f"demo_{random_suffix}"
            password = secrets.token_urlsafe(16)
            user = User.objects.create_user(
                username=username,
                password=password,
                email=f"{username}@demo-invalid.com",
            )

            ttl_hours = settings.DEMO_USER_TTL_HOURS
            demo_expires_at = timezone.now() + timedelta(hours=ttl_hours)

            # Mark user as demo + set expiry
            update_fields = []
            if hasattr(user, "is_demo"):
                user.is_demo = True
                update_fields.append("is_demo")
            if hasattr(user, "demo_expires_at"):
                user.demo_expires_at = demo_expires_at
                update_fields.append("demo_expires_at")
            user.save(update_fields=update_fields or None)

            # Assign group if not a customer (customers don't belong to one)
            if role_enum != Role.CUSTOMER:
                group, _ = Group.objects.get_or_create(
                    name=role_enum.label
                )  # "Manager" / "Delivery crew"
                user.groups.add(group)

        # Issue JWTs and ensure they never outlive the demo account or
        # the global token lifetime limits
        refresh = RefreshToken.for_user(user)
        remaining = (demo_expires_at - timezone.now()).total_seconds()
        refresh.set_exp(
            lifetime=min(
                settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
                timedelta(seconds=remaining),
            )
        )
        access = refresh.access_token
        access.set_exp(
            lifetime=min(
                settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                timedelta(seconds=remaining),
            )
        )

        role = role_enum.value
        data = {
            "detail": f"Temporary '{role}' account created. Expires in {ttl_hours}h.",
            "user": {
                "username": user.username,
                "role": role,
                "expires_at": demo_expires_at.isoformat(),
            },
            "auth": {
                "refresh": str(refresh),
                "access": str(access),
            },
        }
        return Response(data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Demo Authentication"],
    summary="Retrieve the current demo user's profile.",
)
class DemoMeView(APIView):
    """
    Returns the authenticated demo user's profile and TTL information.
    """

    permission_classes = [IsAuthenticated, IsActiveDemo]
    throttle_scope = "auth_me"
    serializer_class = DemoMeSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Demo Authentication"],
    summary="Refresh the access token for a demo user.",
)
class DemoTokenRefreshView(TokenRefreshView):
    """
    Takes a refresh token and returns an access type JSON web token
    if the refresh token is valid and the demo user hasn't expired.
    """

    permission_classes = [AllowAny]
    throttle_scope = "auth_refresh"
    serializer_class = DemoSafeTokenRefreshSerializer


@extend_schema(
    tags=["Demo Authentication"],
    summary="Blacklist the refresh token for a demo user.",
    description="Takes a refresh token and blacklists it.",
    responses={200: SimpleDetailSerializer},
)
class DemoLogoutView(APIView):
    """
    Takes a refresh token and blacklists it. Used with the
    `rest_framework_simplejwt.token_blacklist` app installed.
    """

    permission_classes = [IsAuthenticated, IsActiveDemo]
    throttle_scope = "auth_logout"
    serializer_class = DemoLogoutSerializer

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
