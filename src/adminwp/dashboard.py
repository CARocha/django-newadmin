"""Request-scoped extension point for the admin's main dashboard."""

from collections.abc import Mapping
from dataclasses import dataclass

from django.core.exceptions import ImproperlyConfigured
from django.forms import Media
from django.forms.widgets import MediaDefiningClass
from django.utils.module_loading import import_string

from adminwp.conf import get_options


class Dashboard(metaclass=MediaDefiningClass):
    """Provide a template, request data and optional Media for the admin index."""

    template_name = "adminwp/dashboard/layout.html"
    permissions = ()

    def has_permission(self, request):
        return (
            request.user.is_active
            and request.user.is_staff
            and request.user.has_perms(self.permissions)
        )

    def get_context_data(self, request):
        return {}


class EChartsDashboard(Dashboard):
    """Opt in to the packaged, local Apache ECharts runtime and adapter."""

    class Media:
        js = ["adminwp/vendor/echarts/echarts.min.js", "adminwp/js/dashboard-charts.js"]


@dataclass
class _ResolvedDashboard:
    template_name: str
    data: Mapping
    media: Media


def resolve_dashboard(request):
    """Resolve once per request; permission checks precede data and Media evaluation."""
    if hasattr(request, "_adminwp_dashboard"):
        return request._adminwp_dashboard
    site_name = getattr(request, "current_app", None) or getattr(
        getattr(request, "resolver_match", None), "namespace", None
    )
    path = get_options(site_name)["DASHBOARD"]
    result = None
    if path is not None:
        try:
            provider_class = import_string(path)
        except (ImportError, AttributeError) as exc:
            raise ImproperlyConfigured(f"ADMINWP.DASHBOARD cannot import {path!r}.") from exc
        if not isinstance(provider_class, type) or not issubclass(provider_class, Dashboard):
            raise ImproperlyConfigured("ADMINWP.DASHBOARD must name a Dashboard subclass.")
        provider = provider_class()
        if provider.has_permission(request):
            data = provider.get_context_data(request)
            if not isinstance(data, Mapping):
                raise ImproperlyConfigured("ADMINWP.DASHBOARD context must be a mapping.")
            if not isinstance(provider.template_name, str) or not provider.template_name:
                raise ImproperlyConfigured(
                    "ADMINWP.DASHBOARD template_name must be non-empty text."
                )
            result = _ResolvedDashboard(provider.template_name, data, provider.media)
    request._adminwp_dashboard = result
    return result
