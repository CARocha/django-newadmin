from django import template
from django.utils.html import format_html

from adminwp.conf import get_options

try:
    from django.utils.csp import nonce_attr
except ImportError:  # Django 6.0 predates the built-in CSP nonce helpers.
    nonce_attr = None

register = template.Library()


@register.simple_tag(takes_context=True)
def adminwp_options(context):
    request = context.get("request")
    match = getattr(request, "resolver_match", None)
    site_name = getattr(match, "namespace", None)
    return get_options(site_name)


@register.simple_tag(takes_context=True)
def adminwp_ordered_apps(context, apps):
    request = context.get("request")
    match = getattr(request, "resolver_match", None)
    options = get_options(getattr(match, "namespace", None))
    order = options["MENU"]["ORDER"]
    positions = {app_label: index for index, app_label in enumerate(order)}
    return sorted(
        apps,
        key=lambda app: positions.get(app["app_label"], len(positions)),
    )


@register.simple_tag(takes_context=True)
def adminwp_nonce_attr(context):
    """Render Django's CSP nonce attribute when the current request has one."""
    if nonce_attr is not None:
        return nonce_attr(context)
    nonce = context.get("csp_nonce")
    return format_html('nonce="{}"', nonce) if nonce is not None else ""
