"""Django system checks for common NewAdmin configuration errors."""

from django.conf import settings
from django.core.checks import Error, register
from django.core.exceptions import ImproperlyConfigured

from newadmin.conf import get_options


@register("admin")
def check_newadmin(app_configs, **kwargs):
    errors = []
    installed_apps = getattr(settings, "INSTALLED_APPS", [])
    if "newadmin" in installed_apps and "django.contrib.admin" in installed_apps:
        if installed_apps.index("newadmin") > installed_apps.index("django.contrib.admin"):
            errors.append(
                Error(
                    "Add 'newadmin' before 'django.contrib.admin' in INSTALLED_APPS.",
                    id="newadmin.E005",
                )
            )
    try:
        options = get_options()
        for site_name in options["SITES"]:
            get_options(site_name)
    except ImproperlyConfigured as exc:
        errors.append(Error(str(exc), id=getattr(exc, "check_id", "newadmin.E002")))
    return errors
