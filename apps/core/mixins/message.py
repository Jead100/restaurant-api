from django.utils.translation import gettext_lazy as _

DEFAULT_RESOURCE_NAME = "Item"


class ResourceNameMixin:
    """
    Provides singular and plural labels for a view resource.

    They may be set on the view like so:
        resource_name = "Category"
        resource_plural_name = "Categories"

    Defaults to "Item" and "Items" if not explicitly set.
    Fallback for singular name is defined by DEFAULT_RESOURCE_NAME.
    """

    def get_resource_name(self) -> str:
        return getattr(self, "resource_name", DEFAULT_RESOURCE_NAME)

    def get_resource_plural_name(self) -> str:
        return getattr(self, "resource_plural_name", f"{self.get_resource_name()}s")


DEFAULT_SUCCESS_MESSAGES = {
    "list": _("{resource_plural}"),
    "retrieve": _("{resource} details"),
    "create": _("{resource} created successfully."),
    "update": _("{resource}{adverb} updated successfully."),
    "destroy": _("{resource} deleted successfully."),
}


class ResponseMessageMixin(ResourceNameMixin):
    """
    Provides localized success messages for CRUD actions.

    Uses `msg(action, **kwargs)` to return a formatted message.
    Falls back to `default_messages` if no `<action>_message` is defined.

    Templates use context from `get_msg_context()`, including:
    - resource / resource_plural (defaults to "Item" / "Items")

    Example:
        self.msg("update", adverb="partially") ->
        "Item partially updated successfully."

    Views may define `<action>_message`, override `default_messages`,
    or extend `get_msg_context()` to customize output.
    """

    default_messages = DEFAULT_SUCCESS_MESSAGES.copy()

    def msg(self, action: str, **kwargs) -> str:
        tmpl = getattr(self, f"{action}_message", None)  # per-view override
        if tmpl is None:
            tmpl = self.default_messages.get(action)  # global default
        if not tmpl:
            return ""

        # Merge global and caller-provided context
        context = {**self.get_msg_context(), **kwargs}
        return tmpl.format(**context)

    def get_msg_context(self) -> dict:
        """
        Default context variables for message formatting.
        """
        return {
            "resource": self.get_resource_name(),
            "resource_plural": self.get_resource_plural_name(),
        }
