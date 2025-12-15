from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from ..serializers import UserSerializer


@extend_schema(tags=["Authentication"])
class CurrentUserView(APIView):
    """
    Returns the authenticated user's profile.
    Mirrors Djoser's /users/me/ endpoint.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
