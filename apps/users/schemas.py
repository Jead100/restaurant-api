from apps.core.schemas import BaseEnvelopeSerializer
from apps.users.serializers import UserTinySerializer

from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema, extend_schema_serializer


@extend_schema_serializer(component_name="UserTinyEnvelope")
class UserTinyEnvelopeSerializer(BaseEnvelopeSerializer):
    """
    Envelope schema for user objects
    """

    data = UserTinySerializer(
        help_text="User resource",
        read_only=True,
    )


class DjoserUserViewSetExtension(OpenApiViewExtension):
    """
    Extends Djoser's UserViewSet schema by adding the "Authentication" tag.
    """

    target_class = "djoser.views.UserViewSet"

    def view_replacement(self):
        from djoser.views import UserViewSet

        return extend_schema(tags=["Authentication"])(UserViewSet)
