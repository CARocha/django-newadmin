from django.contrib.staticfiles import finders
from django.test import Client, override_settings


def test_appearance_controller_and_bootstrap_are_packaged():
    assert finders.find("adminwp/js/appearance.js") is not None
    assert finders.find("adminwp/css/bootstrap.min.css") is not None


@override_settings(ADMINWP={"DEFAULT_MODE": "dark"})
def test_admin_uses_configured_default_mode_for_appearance_controller():
    response = Client().get("/admin/login/")

    assert response.status_code == 200
    assert b"adminwp/js/appearance.js" in response.content
    assert b'data-default-mode="dark"' in response.content
