from django import template

from adminwp.conf import get_options

register = template.Library()


@register.simple_tag(takes_context=True)
def adminwp_options(context):
    request = context.get("request")
    match = getattr(request, "resolver_match", None)
    site_name = getattr(match, "namespace", None)
    return get_options(site_name)
