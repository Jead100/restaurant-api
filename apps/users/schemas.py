from apps.core.schemas import BaseEnvelopeSerializer
from apps.users.serializers import UserSerializer

from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema, extend_schema_serializer


@extend_schema_serializer(component_name="UserEnvelope")
class UserEnvelopeSerializer(BaseEnvelopeSerializer):
    """
    Envelope schema for user objects
    """

    data = UserSerializer(
        help_text="User resource",
        read_only=True,
    )


# The following extensions adjust third-party view
# schemas by adding the "Authentication" tag.


class DjoserUserViewSetExtension(OpenApiViewExtension):
    target_class = "djoser.views.UserViewSet"

    def view_replacement(self):
        from djoser.views import UserViewSet

        return extend_schema(tags=["Authentication"])(UserViewSet)


class SimpleJWTObtainExtension(OpenApiViewExtension):
    target_class = "rest_framework_simplejwt.views.TokenObtainPairView"

    def view_replacement(self):
        from rest_framework_simplejwt.views import TokenObtainPairView

        return extend_schema(tags=["Authentication"])(TokenObtainPairView)


class SimpleJWTRefreshExtension(OpenApiViewExtension):
    target_class = "rest_framework_simplejwt.views.TokenRefreshView"

    def view_replacement(self):
        from rest_framework_simplejwt.views import TokenRefreshView

        return extend_schema(tags=["Authentication"])(TokenRefreshView)


class SimpleJWTVerifyExtension(OpenApiViewExtension):
    target_class = "rest_framework_simplejwt.views.TokenVerifyView"

    def view_replacement(self):
        from rest_framework_simplejwt.views import TokenVerifyView

        return extend_schema(tags=["Authentication"])(TokenVerifyView)
