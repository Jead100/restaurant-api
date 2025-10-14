from rest_framework.exceptions import ValidationError


class StrictFieldsMixin:
    """
    Reject any payload keys that are not explicitly declared in `self.fields`.
    """

    def validate(self, attrs):
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise ValidationError({k: ["Unexpected field."] for k in unknown})
        return super().validate(attrs)
