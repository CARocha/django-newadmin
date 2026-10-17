from copy import deepcopy

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import override_settings
from django.urls import reverse

pytestmark = pytest.mark.django_db


@override_settings(
    ADMINWP={
        "MENU": {
            "LINKS": [
                {
                    "LABEL": "Reports",
                    "URL_NAME": "admin:catalog_article_changelist",
                    "ICON": "chart",
                    "PERMISSIONS": ["catalog.view_article"],
                }
            ],
            "ICONS": {"catalog": "folder", "catalog.article": "file-text"},
        }
    }
)
def test_custom_menu_links_resolve_in_the_current_admin_namespace_and_check_permissions(client):
    user = get_user_model().objects.create_user("reader", password="secret", is_staff=True)
    permission = Permission.objects.get(codename="view_article")
    user.user_permissions.add(permission)
    client.force_login(user)

    response = client.get(reverse("operations:index"))

    assert response.status_code == 200
    assert b"Reports" in response.content
    assert b'href="/operations/catalog/article/"' in response.content
    assert client.get(reverse("admin:index")).status_code == 200


@override_settings(
    ADMINWP={
        "MENU": {
            "LINKS": [
                {
                    "LABEL": "Reports",
                    "URL_NAME": "report",
                    "PERMISSIONS": ["catalog.view_article"],
                }
            ]
        }
    }
)
def test_custom_menu_link_is_hidden_when_permission_is_missing(client):
    user = get_user_model().objects.create_user("reader", password="secret", is_staff=True)
    client.force_login(user)

    response = client.get(reverse("admin:index"))

    assert response.status_code == 200
    assert b"Reports" not in response.content


@override_settings(ADMINWP={"CUSTOM_CSS": ["branding/adminwp-extra.css"]})
def test_custom_static_assets_are_rendered_after_adminwp_styles(client):
    response = client.get("/admin/login/")
    content = response.content.decode()

    assert content.index("adminwp/css/adminwp.css") < content.index("branding/adminwp-extra.css")


def test_consumer_templates_media_and_last_stylesheet_are_preserved(client, settings, monkeypatch):
    from django.contrib import admin

    from demo.catalog.models import Article

    settings.ADMINWP = {"CUSTOM_CSS": ["branding/adminwp-extra.css"]}
    templates = deepcopy(settings.TEMPLATES)
    templates[0]["APP_DIRS"] = False
    templates[0]["OPTIONS"]["loaders"] = [
        (
            "django.template.loaders.locmem.Loader",
            {
                "admin/base_site.html": '{% extends "admin/base_site.html" %}'
                "{% block adminwp_branding %}{{ block.super }}"
                '<span id="consumer-branding">Studio</span>{% endblock %}'
                '{% block adminwp_footer %}<span id="consumer-footer">Help</span>{% endblock %}',
                "admin/nav_sidebar.html": '{% extends "admin/nav_sidebar.html" %}'
                "{% block adminwp_sidebar_extra %}{{ block.super }}"
                '<a id="consumer-sidebar" href="/reports/">Custom report</a>{% endblock %}',
            },
        ),
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    ]

    settings.TEMPLATES = templates

    class Media:
        css = {"all": ["branding/editor.css"]}
        js = ["branding/editor.js"]

    monkeypatch.setattr(type(admin.site._registry[Article]), "Media", Media, raising=False)
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)
    content = client.get(reverse("admin:catalog_article_add")).content.decode()
    assert 'id="consumer-branding"' in content
    assert 'id="consumer-footer"' in content
    assert 'id="consumer-sidebar"' in content
    assert content.count('src="/static/branding/editor.js"') == 1
    assert content.count('href="/static/branding/editor.css"') == 1
    for resource in ("admin/css/forms.css", "admin/css/autocomplete.css", "branding/editor.css"):
        assert content.index(resource) < content.index("branding/adminwp-extra.css")


@pytest.mark.parametrize("viewname", ["no_such_view", "admin:auth_user_changelist"])
def test_unresolvable_links_do_not_fall_back_to_another_site(client, settings, viewname):
    from django.core.exceptions import ImproperlyConfigured

    settings.ADMINWP = {"MENU": {"LINKS": [{"LABEL": "Reports", "URL_NAME": viewname}]}}
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)
    with pytest.raises(ImproperlyConfigured, match="MENU.LINKS"):
        client.get(reverse("operations:index"))


def test_link_labels_are_lazy_translatable_and_escaped(client, settings):
    from django.utils.translation import gettext_lazy

    settings.ADMINWP = {
        "MENU": {
            "LINKS": [
                {
                    "LABEL": gettext_lazy("<img src=x onerror=alert(1)>"),
                    "URL_NAME": "report",
                }
            ]
        }
    }
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)
    content = client.get(reverse("admin:index")).content.decode()
    assert "&lt;img src=x onerror=alert(1)&gt;" in content
    assert "<img src=x" not in content


def test_link_requires_every_declared_permission(client, settings):
    settings.ADMINWP = {
        "MENU": {
            "LINKS": [
                {
                    "LABEL": "Restricted reports",
                    "URL_NAME": "report",
                    "PERMISSIONS": ["catalog.view_article", "catalog.view_category"],
                }
            ]
        }
    }
    user = get_user_model().objects.create_user("partial", password="secret", is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="view_article"))
    client.force_login(user)
    assert b"Restricted reports" not in client.get(reverse("admin:index")).content
    user.user_permissions.add(Permission.objects.get(codename="view_category"))
    assert b"Restricted reports" in client.get(reverse("admin:index")).content


def test_current_link_handles_non_ascii_paths(settings):
    from django.test import RequestFactory
    from django.urls import resolve

    from adminwp.navigation import custom_links

    settings.ADMINWP = {"MENU": {"LINKS": [{"LABEL": "Niñez", "URL_NAME": "unicode-report"}]}}
    url = reverse("unicode-report")
    request = RequestFactory().get(url)
    request.resolver_match = resolve(request.path)
    assert custom_links(request)[0]["current"] is True
