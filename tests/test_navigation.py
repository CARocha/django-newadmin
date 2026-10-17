import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

pytestmark = pytest.mark.django_db


@override_settings(ADMINWP={"MENU": {"ORDER": ["catalog", "auth"]}})
def test_navigation_orders_authorized_apps_first(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)

    response = client.get(reverse("admin:index"))
    content = response.content.decode()

    sidebar = content.split('id="nav-sidebar"', 1)[1]
    assert sidebar.index("Editorial") < sidebar.index("Authentication and Authorization")


def test_navigation_only_renders_models_the_user_can_access(client):
    user = get_user_model().objects.create_user("reader", password="secret", is_staff=True)
    permission = user.user_permissions.model.objects.get(codename="view_article")
    user.user_permissions.add(permission)
    client.force_login(user)

    response = client.get(reverse("admin:index"))

    assert response.status_code == 200
    assert b"Articles" in response.content
    assert b"Categories" not in response.content
    assert b"Users" not in response.content
    assert reverse("admin:catalog_article_add").encode() not in response.content


def test_navigation_marks_the_current_model_and_keeps_the_native_toggle(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)

    response = client.get(reverse("admin:catalog_article_changelist"))

    assert b'aria-label="Toggle navigation"' in response.content
    assert b'aria-current="page">Articles</a>' in response.content
