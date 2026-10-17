"""Validated settings for AdminWP."""

from collections.abc import Mapping
from copy import deepcopy

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DEFAULTS = {
    "SITE_TITLE": None,
    "SITE_HEADER": None,
    "LOGO": None,
    "DEFAULT_MODE": "auto",
    "PALETTE": "sapphire",
    "MENU": {"ORDER": [], "ICONS": {}, "LINKS": []},
    "CUSTOM_CSS": [],
    "DASHBOARD": None,
    "SITES": {},
}
VALID_MODES = {"light", "dark", "auto"}


def _merge(base, overrides):
    result = deepcopy(base)
    for key, value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, Mapping):
            result[key] = _merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _validate_resource_path(value, option):
    if value is None and option == "LOGO":
        return
    paths = [value] if option == "LOGO" else value
    if option == "CUSTOM_CSS" and not isinstance(paths, list):
        raise ImproperlyConfigured("ADMINWP.CUSTOM_CSS must be a list of static paths.")
    for path in paths:
        if (
            not isinstance(path, str)
            or not path
            or path.startswith(("/", "\\"))
            or ".." in path.split("/")
            or "\\" in path
            or any(char in path for char in (":", "?", "#"))
        ):
            raise ImproperlyConfigured(f"ADMINWP.{option} must contain safe relative static paths.")


def get_options(site_name=None):
    """Return a fresh, validated settings mapping for an optional AdminSite."""
    raw = getattr(settings, "ADMINWP", {})
    if not isinstance(raw, Mapping):
        raise ImproperlyConfigured("ADMINWP must be a mapping of supported options.")
    unknown = set(raw) - set(DEFAULTS)
    if unknown:
        raise ImproperlyConfigured(f"Unknown ADMINWP option(s): {', '.join(sorted(unknown))}.")

    options = _merge(DEFAULTS, raw)
    if not isinstance(options["SITES"], Mapping):
        raise ImproperlyConfigured("ADMINWP.SITES must be a mapping of AdminSite names to options.")
    if site_name is not None and site_name in options["SITES"]:
        site_options = options["SITES"][site_name]
        if not isinstance(site_options, Mapping):
            raise ImproperlyConfigured(f"ADMINWP.SITES.{site_name} must be a mapping.")
        unknown_site = set(site_options) - (set(DEFAULTS) - {"SITES"})
        if unknown_site:
            raise ImproperlyConfigured(
                f"Unknown ADMINWP.SITES.{site_name} option(s): {', '.join(sorted(unknown_site))}."
            )
        options = _merge(options, site_options)

    if not isinstance(options["DEFAULT_MODE"], str) or options["DEFAULT_MODE"] not in VALID_MODES:
        raise ImproperlyConfigured("ADMINWP.DEFAULT_MODE must be 'light', 'dark', or 'auto'.")
    if options["PALETTE"] != "sapphire":
        raise ImproperlyConfigured("ADMINWP.PALETTE must be 'sapphire'.")
    _validate_resource_path(options["LOGO"], "LOGO")
    _validate_resource_path(options["CUSTOM_CSS"], "CUSTOM_CSS")
    if options["DASHBOARD"] is not None and (
        not isinstance(options["DASHBOARD"], str) or not options["DASHBOARD"].strip()
    ):
        raise ImproperlyConfigured("ADMINWP.DASHBOARD must be an importable class path or None.")
    if not isinstance(options["MENU"], Mapping):
        raise ImproperlyConfigured("ADMINWP.MENU must be a mapping.")
    menu_keys = {"ORDER", "ICONS", "LINKS"}
    unknown_menu_keys = set(options["MENU"]) - menu_keys
    if unknown_menu_keys:
        raise ImproperlyConfigured(
            f"Unknown ADMINWP.MENU option(s): {', '.join(sorted(unknown_menu_keys))}."
        )
    order = options["MENU"].get("ORDER", [])
    if not isinstance(order, list) or any(not isinstance(label, str) for label in order):
        raise ImproperlyConfigured("ADMINWP.MENU.ORDER must be a list of app labels.")
    if len(order) != len(set(order)):
        raise ImproperlyConfigured("ADMINWP.MENU.ORDER cannot contain duplicate app labels.")
    for name in ("SITE_TITLE", "SITE_HEADER"):
        if options[name] is not None and not isinstance(options[name], str):
            raise ImproperlyConfigured(f"ADMINWP.{name} must be text or None.")
    return options
