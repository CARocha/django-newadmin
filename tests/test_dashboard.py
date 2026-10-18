import pytest
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.auth import get_user_model
from django.urls import reverse

from demo.catalog.models import Article

pytestmark = pytest.mark.django_db


def test_dashboard_groups_accessible_models_into_cards_and_shows_recent_actions(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    article = Article.objects.create(title="A dashboard story", slug="dashboard-story")
    LogEntry.objects.log_actions(
        user.pk,
        Article.objects.filter(pk=article.pk),
        ADDITION,
    )
    client.force_login(user)

    response = client.get(reverse("admin:index"))
    content = response.content.decode()

    assert response.status_code == 200
    assert 'class="newadmin-dashboard"' in content
    assert 'class="newadmin-dashboard__card"' in content
    assert 'href="/admin/catalog/article/"' in content
    assert 'href="/admin/catalog/article/add/"' in content
    assert article.title in content
    assert "Recent actions" in content


def test_dashboard_hides_add_shortcuts_without_add_permission(client):
    user = get_user_model().objects.create_user("reader", password="secret", is_staff=True)
    permission = user.user_permissions.model.objects.get(codename="view_article")
    user.user_permissions.add(permission)
    client.force_login(user)

    response = client.get(reverse("admin:index"))

    assert response.status_code == 200
    assert b' href="/admin/catalog/article/"' in response.content
    assert b'href="/admin/catalog/article/add/"' not in response.content
    assert b"Recent actions" in response.content
