"""Validated settings for NewAdmin."""

from collections.abc import Mapping
from copy import deepcopy

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import Promise

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
ICON_NAMES = {
    "grid",
    "file-text",
    "users",
    "settings",
    "folder",
    "image",
    "calendar",
    "chart",
    "tag",
    "database",
    "globe",
    "link",
}


class _SettingsError(ImproperlyConfigured):
    check_id = "newadmin.E001"


class _ResourceError(ImproperlyConfigured):
    check_id = "newadmin.E003"


class _MenuError(ImproperlyConfigured):
    check_id = "newadmin.E004"


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
        raise _ResourceError("NEWADMIN.CUSTOM_CSS must be a list of static paths.")
    for path in paths:
        if (
            not isinstance(path, str)
            or not path
            or path.startswith(("/", "\\"))
            or ".." in path.split("/")
            or "\\" in path
            or any(char in path for char in (":", "?", "#"))
        ):
            raise _ResourceError(f"NEWADMIN.{option} must contain safe relative static paths.")


def get_options(site_name=None):
    """Return a fresh, validated settings mapping for an optional AdminSite."""
    raw = getattr(settings, "NEWADMIN", {})
    if not isinstance(raw, Mapping):
        raise _SettingsError("NEWADMIN must be a mapping of supported options.")
    unknown = set(raw) - set(DEFAULTS)
    if unknown:
        raise ImproperlyConfigured(
            f"Unknown NEWADMIN option(s): {', '.join(sorted(map(str, unknown)))}."
        )

    options = _merge(DEFAULTS, raw)
    if not isinstance(options["SITES"], Mapping):
        raise _SettingsError("NEWADMIN.SITES must be a mapping of AdminSite names to options.")
    if site_name is not None and site_name in options["SITES"]:
        site_options = options["SITES"][site_name]
        if not isinstance(site_options, Mapping):
            raise _SettingsError(f"NEWADMIN.SITES.{site_name} must be a mapping.")
        unknown_site = set(site_options) - (set(DEFAULTS) - {"SITES"})
        if unknown_site:
            raise ImproperlyConfigured(
                f"Unknown NEWADMIN.SITES.{site_name} option(s): "
                f"{', '.join(sorted(map(str, unknown_site)))}."
            )
        options = _merge(options, site_options)

    if not isinstance(options["DEFAULT_MODE"], str) or options["DEFAULT_MODE"] not in VALID_MODES:
        raise ImproperlyConfigured("NEWADMIN.DEFAULT_MODE must be 'light', 'dark', or 'auto'.")
    if options["PALETTE"] != "sapphire":
        raise ImproperlyConfigured("NEWADMIN.PALETTE must be 'sapphire'.")
    _validate_resource_path(options["LOGO"], "LOGO")
    _validate_resource_path(options["CUSTOM_CSS"], "CUSTOM_CSS")
    if options["DASHBOARD"] is not None and (
        not isinstance(options["DASHBOARD"], str) or not options["DASHBOARD"].strip()
    ):
        raise ImproperlyConfigured("NEWADMIN.DASHBOARD must be an importable class path or None.")
    if not isinstance(options["MENU"], Mapping):
        raise _MenuError("NEWADMIN.MENU must be a mapping.")
    menu_keys = {"ORDER", "ICONS", "LINKS"}
    unknown_menu_keys = set(options["MENU"]) - menu_keys
    if unknown_menu_keys:
        raise _MenuError(
            f"Unknown NEWADMIN.MENU option(s): {', '.join(sorted(map(str, unknown_menu_keys)))}."
        )
    order = options["MENU"].get("ORDER", [])
    if not isinstance(order, list) or any(not isinstance(label, str) for label in order):
        raise _MenuError("NEWADMIN.MENU.ORDER must be a list of app labels.")
    if len(order) != len(set(order)):
        raise _MenuError("NEWADMIN.MENU.ORDER cannot contain duplicate app labels.")
    icons = options["MENU"].get("ICONS", {})
    if not isinstance(icons, Mapping):
        raise _MenuError("NEWADMIN.MENU.ICONS must map app/model names to icon names.")
    for key, icon in icons.items():
        if (
            not isinstance(key, str)
            or not key
            or not isinstance(icon, str)
            or icon not in ICON_NAMES
        ):
            raise _MenuError(f"NEWADMIN.MENU.ICONS.{key} must use a supported icon name.")
    links = options["MENU"].get("LINKS", [])
    if not isinstance(links, list):
        raise _MenuError("NEWADMIN.MENU.LINKS must be a list of link mappings.")
    for index, link in enumerate(links):
        path = f"NEWADMIN.MENU.LINKS[{index}]"
        if not isinstance(link, Mapping):
            raise _MenuError(f"{path} must be a mapping.")
        unknown_link = set(link) - {"LABEL", "URL_NAME", "ICON", "PERMISSIONS"}
        if unknown_link:
            raise _MenuError(
                f"{path} has unknown option(s): {', '.join(sorted(map(str, unknown_link)))}."
            )
        for key in ("LABEL", "URL_NAME"):
            types = (str, Promise) if key == "LABEL" else str
            if not isinstance(link.get(key), types) or not str(link[key]).strip():
                raise _MenuError(f"{path}.{key} must be non-empty text.")
        if "ICON" in link and (not isinstance(link["ICON"], str) or link["ICON"] not in ICON_NAMES):
            raise _MenuError(f"{path}.ICON must name a supported icon.")
        permissions = link.get("PERMISSIONS", [])
        if not isinstance(permissions, list) or any(
            not isinstance(permission, str)
            or permission.count(".") != 1
            or not all(permission.split("."))
            or any(char.isspace() for char in permission)
            for permission in permissions
        ):
            raise _MenuError(f"{path}.PERMISSIONS must be a list of app.codename values.")
    for name in ("SITE_TITLE", "SITE_HEADER"):
        if options[name] is not None and not isinstance(options[name], str):
            raise ImproperlyConfigured(f"NEWADMIN.{name} must be text or None.")
    return options
