from django.apps import AppConfig
from django.contrib.staticfiles import finders
from django.template import loader
from django.test import Client


def test_django_can_discover_the_newadmin_app():
    app_config = AppConfig.create("newadmin")

    assert app_config.name == "newadmin"
    assert app_config.label == "newadmin"


def test_admin_base_site_is_extended_by_the_packaged_template():
    template = loader.get_template("admin/base_site.html")

    assert template.origin.name.endswith("newadmin/templates/admin/base_site.html")


def test_theme_stylesheet_is_available_through_staticfiles():
    stylesheet = finders.find("newadmin/css/newadmin.css")

    assert stylesheet is not None


def test_admin_login_includes_the_theme_stylesheet():
    response = Client().get("/admin/login/")

    assert response.status_code == 200
    assert b"newadmin/css/newadmin.css" in response.content


def test_echarts_distribution_includes_runtime_license_and_notice():
    for filename in (
        "echarts.min.js",
        "LICENSE",
        "NOTICE",
        "licenses/LICENSE-d3",
        "licenses/LICENSE-zrender",
        "licenses/LICENSE-tslib",
        "licenses/NOTICE-tslib",
    ):
        assert finders.find(f"newadmin/vendor/echarts/{filename}") is not None


def test_icon_catalog_has_a_packaged_symbol_for_each_allowed_identifier():
    from pathlib import Path
    from xml.etree import ElementTree

    from newadmin.conf import ICON_NAMES

    sprite = finders.find("newadmin/icons.svg")
    assert sprite is not None
    tree = ElementTree.fromstring(Path(sprite).read_text())
    assert {symbol.attrib["id"] for symbol in tree} == ICON_NAMES
    for name in ("bootstrap-icons", "django"):
        assert finders.find(f"newadmin/vendor/{name}/LICENSE") is not None


def test_bootstrap_css_license_is_available_to_consumers():
    assert finders.find("newadmin/vendor/bootstrap/LICENSE") is not None
