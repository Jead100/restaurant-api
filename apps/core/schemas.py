from rest_framework import serializers


class BaseEnvelopeSerializer(serializers.Serializer):
    """
    Base serializer for a standardized `{detail, data}` response envelope
    used in OpenAPI response schemas.

    Example:
        {
            "detail": "Success",
            "data": { ... }
        }

    Subclasses should override `data` with a concrete serializer
    to define the response payload shape for a given endpoint.
    """

    detail = serializers.CharField(
        default="success message",
        help_text="Human-readable status message",
        read_only=True,
    )

    data = serializers.JSONField(
        help_text="Response payload (object, list, or primitive).",
        read_only=True,
    )


class SimpleDetailSerializer(serializers.Serializer):
    """
    Schema for actions that only return a detail message.
    """

    detail = serializers.CharField(
        default="success message",
        help_text="Human-readable status message",
        read_only=True,
    )
