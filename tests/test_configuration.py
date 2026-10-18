import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from newadmin.checks import check_newadmin
from newadmin.conf import DEFAULTS, get_options


def test_configuration_has_documented_defaults():
    assert get_options() == DEFAULTS


@override_settings(NEWADMIN={"SITE_HEADER": "Studio", "MENU": {"ORDER": ["catalog"]}})
def test_configuration_merges_partial_overrides():
    options = get_options()

    assert options["SITE_HEADER"] == "Studio"
    assert options["MENU"]["ORDER"] == ["catalog"]
    assert options["MENU"]["ICONS"] == {}


@override_settings(NEWADMIN={"SITES": {"operations": {"SITE_HEADER": "Operations"}}})
def test_configuration_resolves_per_site_branding_without_sharing_mutable_values():
    assert get_options("operations")["SITE_HEADER"] == "Operations"
    assert get_options()["SITE_HEADER"] is None


@override_settings(NEWADMIN={"SITES": {"operations": {"TYPO": "invalid"}}})
def test_system_check_reports_invalid_per_site_options():
    errors = check_newadmin(None)

    assert len(errors) == 1
    assert errors[0].id == "newadmin.E002"


@override_settings(NEWADMIN={"DEFAULT_MODE": "sepia"})
def test_invalid_mode_has_a_clear_error():
    with pytest.raises(ImproperlyConfigured, match="DEFAULT_MODE"):
        get_options()


@override_settings(NEWADMIN={"DEFAULT_MODE": []})
def test_invalid_mode_type_has_a_clear_error():
    with pytest.raises(ImproperlyConfigured, match="DEFAULT_MODE"):
        get_options()


@override_settings(NEWADMIN={"CUSTOM_CSS": ["../outside.css"]})
def test_unsafe_static_paths_are_rejected():
    with pytest.raises(ImproperlyConfigured, match="CUSTOM_CSS"):
        get_options()


@override_settings(NEWADMIN={"SITE_HEADER": "Studio"})
def test_configured_branding_is_rendered_on_the_admin_login(client):
    response = client.get("/admin/login/")

    assert response.status_code == 200
    assert b"Studio" in response.content


@override_settings(NEWADMIN={"SITE_TITLE": "Editorial studio"})
def test_configured_site_title_is_used_in_the_document_title(client):
    response = client.get("/admin/login/")

    assert b"Editorial studio" in response.content


@pytest.mark.parametrize(
    "menu",
    [
        {"ICONS": []},
        {"ICONS": {"catalog": "unknown"}},
        {"LINKS": "Reports"},
        {"LINKS": ["Reports"]},
        {"LINKS": [{"LABEL": "Reports"}]},
        {"LINKS": [{"LABEL": "Reports", "URL_NAME": "report", "ICON": "unknown"}]},
        {"LINKS": [{"LABEL": "Reports", "URL_NAME": "report", "PERMISSIONS": ["view"]}]},
    ],
)
def test_invalid_menu_extensions_fail_clearly(menu):
    with override_settings(NEWADMIN={"MENU": menu}):
        with pytest.raises(ImproperlyConfigured, match="MENU"):
            get_options()


@pytest.mark.parametrize(
    "options, code",
    [
        ([], "newadmin.E001"),
        ({"SITES": []}, "newadmin.E001"),
        ({"MENU": {"ICONS": {"catalog": "unknown"}}}, "newadmin.E004"),
        ({"CUSTOM_CSS": ["../outside.css"]}, "newadmin.E003"),
    ],
)
def test_checks_identify_the_configuration_area(options, code):
    with override_settings(NEWADMIN=options):
        assert check_newadmin(None)[0].id == code
