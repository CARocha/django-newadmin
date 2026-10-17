from django import template
from django.templatetags.static import static
from django.utils.html import format_html

from adminwp.conf import ICON_NAMES, get_options
from adminwp.dashboard import resolve_dashboard
from adminwp.navigation import custom_links, site_name

try:
    from django.utils.csp import nonce_attr
except ImportError:  # Django 6.0 predates the built-in CSP nonce helpers.
    nonce_attr = None

register = template.Library()


@register.simple_tag(takes_context=True)
def adminwp_options(context):
    return get_options(site_name(context.get("request")))


@register.simple_tag(takes_context=True)
def adminwp_ordered_apps(context, apps):
    options = get_options(site_name(context.get("request")))
    order = options["MENU"]["ORDER"]
    positions = {app_label: index for index, app_label in enumerate(order)}
    return sorted(
        apps,
        key=lambda app: positions.get(app["app_label"], len(positions)),
    )


@register.simple_tag(takes_context=True)
def adminwp_nonce_attr(context, media=None):
    """Render Django's CSP nonce attribute when the current request has one."""
    if nonce_attr is not None:
        return nonce_attr(context, media)
    if media is not None:
        return media
    nonce = context.get("csp_nonce")
    return format_html('nonce="{}"', nonce) if nonce is not None else ""


@register.simple_tag(takes_context=True)
def adminwp_dashboard(context):
    request = context["request"]
    if getattr(getattr(request, "resolver_match", None), "url_name", None) != "index":
        return None
    return resolve_dashboard(request)


@register.simple_tag(takes_context=True)
def adminwp_custom_links(context):
    return custom_links(context.get("request"))


@register.simple_tag
def adminwp_icon(icon):
    """A local decorative icon; the adjacent label carries its accessible name."""
    if not isinstance(icon, str) or icon not in ICON_NAMES:
        icon = "file-text"
    return format_html(
        '<svg class="adminwp-icon" aria-hidden="true" focusable="false">'
        '<use href="{}#{}"></use></svg>',
        static("adminwp/icons.svg"),
        icon,
    )


@register.simple_tag(takes_context=True)
def adminwp_model_icon(context, app_label, model_name=None):
    icons = get_options(site_name(context.get("request")))["MENU"]["ICONS"]
    key = f"{app_label}.{model_name}" if model_name else app_label
    return icons.get(key, icons.get(app_label, "file-text" if model_name else "folder"))
