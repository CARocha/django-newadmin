"""Application definition for the AdminWP theme."""

from django.apps import AppConfig


class AdminWPConfig(AppConfig):
    """Register AdminWP as a lightweight Django application."""

    name = "adminwp"
    verbose_name = "Django AdminWP"

    def ready(self):
        from adminwp import checks  # noqa: F401
