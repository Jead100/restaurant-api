from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from core.mixins.message import DEFAULT_RESOURCE_NAME

class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom paginator that adds a localized `detail` message
    to the paginated response.
    """

    page_size = 8  # default page size
    page_query_param = "page"  # allows ?page=2
    page_size_query_param = "perpage"  # allows ?perpage=10
    max_page_size = 100  # maximum allowed page size

    def paginate_queryset(self, queryset, request, view=None):
        """
        Set detail message for the response, using view.msg()
        if available, else fallback to default plural label.
        """
        if view and hasattr(view, "msg"):
            self.detail_msg = view.msg("list")
        else:
            # fallback for views without msg()
            self.detail_msg = f"{DEFAULT_RESOURCE_NAME}s"

        return super().paginate_queryset(queryset, request, view)

    def get_page_details(self):
        """
        Return pagination metadata: count, next, previous links.
        """
        return {
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
        }

    def get_paginated_response(self, data):
        """
        Return a paginated response with `detail`, `data`,
        and pagination metadata.
        """
        return Response(
            {
                "detail": self.detail_msg,
                "data": data,
                **self.get_page_details(),
            },
            status=status.HTTP_200_OK,
        )
