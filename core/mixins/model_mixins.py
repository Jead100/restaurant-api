"""
Thin wrappers over DRF mixins for the restaurant viewsets.

They keep DRF's logic but:

* wrap every result in `format_response`
* re-serialize create/update responses with the read-only
  `res_serializer_cls` when that attribute is set

Each response includes a localized, action-specific message
via `self.msg(action, **kwargs)` from `ResponseMessageMixin`.
"""

from rest_framework import mixins, status

from core.responses import format_response


class CustomListModelMixin:
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return format_response(
            detail=self.msg("list"),
            data=serializer.data,
            status=status.HTTP_200_OK,
        )


class CustomCreateModelMixin(mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        res_serializer_cls = getattr(self, "res_serializer_cls", None)
        if res_serializer_cls is not None:
            res_serializer = self.res_serializer_cls(
                serializer.instance, context=self.get_serializer_context()
            )
            data = res_serializer.data
        else:
            data = serializer.data

        return format_response(
            detail=self.msg("create"),
            data=data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class CustomRetrieveModelMixin:
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return format_response(
            detail=self.msg("retrieve"),
            data=serializer.data,
            status=status.HTTP_200_OK,
        )


class CustomUpdateModelMixin(mixins.UpdateModelMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        adverb = " partially" if partial else ""

        res_serializer_cls = getattr(self, "res_serializer_cls", None)
        if res_serializer_cls is not None:
            res_serializer = self.res_serializer_cls(
                instance, context=self.get_serializer_context()
            )
            data = res_serializer.data
        else:
            data = serializer.data

        return format_response(
            detail=self.msg("update", adverb=adverb),
            data=data,
            status=status.HTTP_200_OK,
        )


class CustomDestroyModelMixin(mixins.DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return format_response(
            detail=self.msg("destroy"),
            data=None,
            status=status.HTTP_200_OK,
        )
