import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_admin_logout_requires_post_and_csrf(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)

    index = client.get(reverse("admin:index"))
    csrf_token = client.cookies["csrftoken"].value

    assert b'id="logout-form" method="post"' in index.content
    assert client.get(reverse("admin:logout")).status_code == 405
    assert client.post(reverse("admin:logout")).status_code == 403
    assert client.post(
        reverse("admin:logout"), HTTP_X_CSRFTOKEN=csrf_token
    ).status_code in {200, 302}
    assert client.get(reverse("admin:index")).status_code == 302


def test_admin_password_change_keeps_session_and_displays_success_message(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)

    response = client.post(
        reverse("admin:password_change"),
        {
            "old_password": "secret",
            "new_password1": "A-new-safe-password-2026",
            "new_password2": "A-new-safe-password-2026",
        },
        follow=True,
    )

    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("admin:password_change_done")
    assert b"Your password was changed." in response.content
    user.refresh_from_db()
    assert user.check_password("A-new-safe-password-2026")
    assert client.get(reverse("admin:index")).status_code == 200
