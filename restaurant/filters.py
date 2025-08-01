import django_filters

from rest_framework import filters
from rest_framework.exceptions import ValidationError

from restaurant.models import Order
from users.utils.roles import get_user_role


class StrictOrderingFilter(filters.OrderingFilter):
    """
    Ordering filter that validates fields strictly and uses a custom
    query parameter `order_by` instead of the default `ordering`.
    """

    ordering_param = "order_by"

    def get_ordering(self, request, queryset, view):
        """
        Validate requested ordering fields.

        Falls back to default ordering if none provided.
        """
        params = request.query_params.get(self.ordering_param)
        if params:
            # parse comma-separated field names
            fields = [param.strip() for param in params.split(",")]

            # get list of allowed fields declared on the view
            valid_fields = [
                field[0]
                for field in self.get_valid_fields(queryset, view, {"request": request})
            ]

            # collect any fields not declared as valid
            invalid_fields = [
                field.lstrip("-")
                for field in fields
                if field.lstrip("-") not in valid_fields
            ]
            if invalid_fields:
                raise ValidationError(
                    {
                        "ordering": [
                            f"Invalid ordering field(s): {', '.join(invalid_fields)}. "
                            f"Expected one of: {', '.join(valid_fields)}."
                        ]
                    }
                )

            return fields

        # No ordering was included
        return self.get_default_ordering(view)


DATE_FILTER_OPTIONS = {
    # enforce ISO-style date inputs
    "input_formats": ["%Y-%m-%d"],
    "error_messages": {"invalid": "Please use the date format YYYY-MM-DD."},
}


class OrderFilter(django_filters.FilterSet):
    """
    FilterSet for `OrderViewSet`, supporting date, price, status,
    user, and delivery crew filters.
    """

    # date filters
    date = django_filters.DateFilter(
        field_name="date", lookup_expr="exact", required=False, **DATE_FILTER_OPTIONS
    )
    date_before = django_filters.DateFilter(
        field_name="date", lookup_expr="lte", **DATE_FILTER_OPTIONS
    )
    date_after = django_filters.DateFilter(
        field_name="date", lookup_expr="gte", **DATE_FILTER_OPTIONS
    )

    # price filters
    total = django_filters.NumberFilter(
        field_name="total",
        lookup_expr="exact",
        label="Exact price (=)",
        method="filter_exact_total",
    )
    min_total = django_filters.NumberFilter(
        field_name="total",
        lookup_expr="gte",
        label="Minimum price (≥)",
        method="filter_min_total",
    )
    max_total = django_filters.NumberFilter(
        field_name="total",
        lookup_expr="lte",
        label="Maximum price (≤)",
        method="filter_max_total",
    )

    # status filter (accepts true/false or 1/0 strings)
    status = django_filters.CharFilter(method="filter_status")

    # user filters (only effective for managers)
    user = django_filters.CharFilter(method="filter_user")
    delivery_crew = django_filters.CharFilter(method="filter_delivery_crew")

    class Meta:
        model = Order
        fields = []

    def _validate_non_negative(self, name, value):
        """
        Reject negative prices with a validation error.
        """
        if value < 0:
            raise ValidationError({name: "Price cannot be negative."})
        return value

    def _role_is_manager(self) -> bool:
        """
        Check if the current user has manager role.
        """
        return get_user_role(self.request.user) == "manager"

    def _filter_by_user_field(self, queryset, field_name: str, value: str):
        """
        Filter by user field: accepts primary key, username, or 'null' (NULL in DB).

        Intended for nullable fields like `delivery_crew`.
        """
        value = value.strip().lower()
        if value.isdigit():
            # filter by primary key
            return queryset.filter(**{field_name: int(value)})

        if value == "null":
            # filter rows where field is NULL
            return queryset.filter(**{f"{field_name}__isnull": True})

        # fallback: filter by username (case-insensitive)
        lookup = f"{field_name}__username__iexact"
        return queryset.filter(**{lookup: value})

    def filter_exact_total(self, queryset, name, value):
        """
        Filter orders with exact total equal to value.
        """
        value = self._validate_non_negative(name, value)
        return queryset.filter(total=value)

    def filter_min_total(self, queryset, name, value):
        """
        Filter orders with total >= value.
        """
        value = self._validate_non_negative(name, value)
        return queryset.filter(total__gte=value)

    def filter_max_total(self, queryset, name, value):
        """
        Filter orders with total <= value.
        """
        value = self._validate_non_negative(name, value)
        return queryset.filter(total__lte=value)

    def filter_status(self, queryset, name, value):
        """
        Filter orders by `status` (boolean) using flexible inputs.
        """
        try:
            value = value.strip().lower()
            mapping = {"true": True, "false": False, "1": True, "0": False}
            return queryset.filter(status=mapping[value])
        except KeyError:
            raise ValidationError(
                {name: "Must be one of: 1, 0, true, false (case-insensitive)"}
            )

    def filter_user(self, queryset, name, value):
        """
        Filter orders by `user` (i.e. customer) ID or username (managers only).
        """
        if not self._role_is_manager():
            return queryset
        return self._filter_by_user_field(queryset, "user", value)

    def filter_delivery_crew(self, queryset, name, value):
        """
        Filter orders by `delivery_crew` ID or username (managers only).
        """
        if not self._role_is_manager():
            return queryset
        return self._filter_by_user_field(queryset, "delivery_crew", value)
