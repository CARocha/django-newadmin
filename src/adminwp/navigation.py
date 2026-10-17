"""Request-specific navigation derived from the active admin site."""

from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch, reverse
from django.utils.encoding import iri_to_uri

from adminwp.conf import get_options


def site_name(request):
    match = getattr(request, "resolver_match", None)
    return getattr(request, "current_app", None) or getattr(match, "namespace", None)


def custom_links(request):
    name = site_name(request)
    options = get_options(name)
    user = getattr(request, "user", None)
    links = []
    for index, item in enumerate(options["MENU"]["LINKS"]):
        if item.get("PERMISSIONS") and (user is None or not user.has_perms(item["PERMISSIONS"])):
            continue
        try:
            url = reverse(item["URL_NAME"], current_app=name)
        except NoReverseMatch as exc:
            raise ImproperlyConfigured(
                f"ADMINWP.MENU.LINKS[{index}].URL_NAME cannot be resolved: {item['URL_NAME']!r}."
            ) from exc
        links.append(
            {
                "label": item["LABEL"],
                "url": url,
                "icon": item.get("ICON", "link"),
                "current": iri_to_uri(getattr(request, "path", "")) == url,
            }
        )
    return links
