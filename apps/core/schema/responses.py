from rest_framework import serializers


def wrapped_response(serializer_class, many=False, detail_text=None, data_text=None):
    """
    Returns a serializer class that wraps a resource object (or list) in a
    `detail` and `data` response envelope for standardized response schemas.

    :param serializer_class: The DRF serializer to wrap inside `data`.
    :param many: Whether the data field is a list of objects.
    :param detail_text: Description for the `detail` field.
    :param data_text: Description for the `data` field.
    :return:
    """
    name = f"Wrapped{serializer_class.__name__}"
    return type(
        name,
        (serializers.Serializer,),
        {
            "detail": serializers.CharField(help_text=detail_text),
            "data": serializer_class(many=many, help_text=data_text),
        },
    )


class SimpleDetailResponseSerializer(serializers.Serializer):
    """
    Schema for DELETE and other actions that only return a detail message.
    """

    detail = serializers.CharField()
