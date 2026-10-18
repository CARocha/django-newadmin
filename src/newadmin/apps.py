"""Application definition for the NewAdmin theme."""

from django.apps import AppConfig


class NewAdminConfig(AppConfig):
    """Register NewAdmin as a lightweight Django application."""

    name = "newadmin"
    verbose_name = "Django NewAdmin"

    def ready(self):
        from newadmin import checks  # noqa: F401
