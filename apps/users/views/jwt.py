from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from drf_spectacular.utils import extend_schema

# Subclassed SimpleJWT views with scoped throttling applied.


@extend_schema(
    tags=["Authentication"],
    summary="Authenticate a user and issue tokens.",
    description=(
        "Authenticates a user with credentials and returns an access and "
        "refresh JSON web token pair."
    ),
)
class JWTCreateView(TokenObtainPairView):
    """
    Issues access/refresh tokens for normal (non-demo) users.
    """

    permission_classes = [AllowAny]
    throttle_scope = "auth_login"


@extend_schema(
    tags=["Authentication"],
    summary="Refresh the access token for a user.",
    description=(
        "Takes a refresh token and returns a new access token "
        "if the refresh token is valid."
    ),
)
class JWTRefreshView(TokenRefreshView):
    """
    Refresh access token using refresh token.
    """

    permission_classes = [AllowAny]
    throttle_scope = "auth_refresh"


@extend_schema(
    tags=["Authentication"],
    summary="Verify a token.",
    description="Takes a JSON web token and verifies whether it is valid.",
)
class JWTVerifyView(TokenVerifyView):
    """
    Verify a token is valid.
    """

    permission_classes = [AllowAny]
    throttle_scope = "auth_verify"
