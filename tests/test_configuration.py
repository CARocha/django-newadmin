import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from adminwp.conf import DEFAULTS, get_options


def test_configuration_has_documented_defaults():
    assert get_options() == DEFAULTS


@override_settings(ADMINWP={"SITE_HEADER": "Studio", "MENU": {"ORDER": ["catalog"]}})
def test_configuration_merges_partial_overrides():
    options = get_options()

    assert options["SITE_HEADER"] == "Studio"
    assert options["MENU"]["ORDER"] == ["catalog"]
    assert options["MENU"]["ICONS"] == {}


@override_settings(ADMINWP={"DEFAULT_MODE": "sepia"})
def test_invalid_mode_has_a_clear_error():
    with pytest.raises(ImproperlyConfigured, match="DEFAULT_MODE"):
        get_options()


@override_settings(ADMINWP={"DEFAULT_MODE": []})
def test_invalid_mode_type_has_a_clear_error():
    with pytest.raises(ImproperlyConfigured, match="DEFAULT_MODE"):
        get_options()


@override_settings(ADMINWP={"CUSTOM_CSS": ["../outside.css"]})
def test_unsafe_static_paths_are_rejected():
    with pytest.raises(ImproperlyConfigured, match="CUSTOM_CSS"):
        get_options()


@override_settings(ADMINWP={"SITE_HEADER": "Studio"})
def test_configured_branding_is_rendered_on_the_admin_login(client):
    response = client.get("/admin/login/")

    assert response.status_code == 200
    assert b"Studio" in response.content


@override_settings(ADMINWP={"SITE_TITLE": "Editorial studio"})
def test_configured_site_title_is_used_in_the_document_title(client):
    response = client.get("/admin/login/")

    assert b"Editorial studio" in response.content
