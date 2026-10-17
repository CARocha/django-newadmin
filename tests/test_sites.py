import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

pytestmark = pytest.mark.django_db


@override_settings(
    ADMINWP={
        "SITE_HEADER": "Global studio",
        "CUSTOM_CSS": ["branding/global.css"],
        "SITES": {
            "operations": {
                "SITE_HEADER": "Operations desk",
                "CUSTOM_CSS": ["branding/operations.css"],
                "MENU": {"ORDER": ["auth", "catalog"]},
            }
        },
    }
)
def test_two_admin_sites_keep_branding_resources_and_namespaces_separate(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)

    operations = client.get(reverse("operations:index"))
    default = client.get(reverse("admin:index"))

    assert operations.status_code == default.status_code == 200
    assert b"Operations desk" in operations.content
    assert b"Global studio" not in operations.content
    assert b'href="/operations/"' in operations.content
    assert b"branding/operations.css" in operations.content
    assert b"branding/global.css" not in operations.content
    assert b"Global studio" in default.content
    assert b"Operations desk" not in default.content
    assert b'href="/admin/"' in default.content
    assert b"branding/global.css" in default.content
    assert b"branding/operations.css" not in default.content
