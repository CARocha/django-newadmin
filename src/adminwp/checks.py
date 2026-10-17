"""Django system checks for common AdminWP configuration errors."""

from django.conf import settings
from django.core.checks import Error, register
from django.core.exceptions import ImproperlyConfigured

from adminwp.conf import get_options


@register("admin")
def check_adminwp(app_configs, **kwargs):
    errors = []
    installed_apps = getattr(settings, "INSTALLED_APPS", [])
    if "adminwp" in installed_apps and "django.contrib.admin" in installed_apps:
        if installed_apps.index("adminwp") > installed_apps.index("django.contrib.admin"):
            errors.append(
                Error(
                    "Add 'adminwp' before 'django.contrib.admin' in INSTALLED_APPS.",
                    id="adminwp.E005",
                )
            )
    try:
        options = get_options()
        for site_name in options["SITES"]:
            get_options(site_name)
    except ImproperlyConfigured as exc:
        errors.append(Error(str(exc), id="adminwp.E002"))
    return errors
