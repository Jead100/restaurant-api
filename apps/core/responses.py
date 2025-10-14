from rest_framework.response import Response


def format_response(
    detail: str, data=None, status: int = 200, headers=None
) -> Response:
    """
    Return a standardized API response with `detail` and optional `data`.

    Example:
        format_response("Created", {"id": 123}, 201).data ->
        {
            'detail': 'Created',
            'data': {'id': 123}
        }
    """
    payload = {"detail": detail}
    if data is not None:
        payload["data"] = data

    return Response(payload, status=status, headers=headers)
