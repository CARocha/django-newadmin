import pytest
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from demo.catalog.models import Article

pytestmark = pytest.mark.django_db


def test_history_shows_recent_admin_log_entries(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    article = Article.objects.create(title="History article", slug="history-article")
    LogEntry.objects.log_actions(
        user.pk,
        Article.objects.filter(pk=article.pk),
        ADDITION,
        single_object=True,
    )
    LogEntry.objects.log_actions(
        user.pk,
        Article.objects.filter(pk=article.pk),
        CHANGE,
        "Updated the headline",
        single_object=True,
    )
    client.force_login(user)

    response = client.get(reverse("admin:catalog_article_history", args=[article.pk]))

    assert response.status_code == 200
    assert b'id="change-history"' in response.content
    assert b"editor" in response.content
    assert b"Updated the headline" in response.content


def test_delete_confirmation_requires_csrf_and_logs_successful_deletion():
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    article = Article.objects.create(title="Delete safely", slug="delete-safely")
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    delete_url = reverse("admin:catalog_article_delete", args=[article.pk])

    confirmation = client.get(delete_url)
    csrf_token = client.cookies["csrftoken"].value

    assert confirmation.status_code == 200
    assert b'name="post" value="yes"' in confirmation.content
    assert client.post(delete_url, {"post": "yes"}).status_code == 403
    assert Article.objects.filter(pk=article.pk).exists()

    response = client.post(
        delete_url,
        {"post": "yes"},
        HTTP_X_CSRFTOKEN=csrf_token,
        follow=True,
    )

    assert response.status_code == 200
    assert not Article.objects.filter(pk=article.pk).exists()
    assert b"success" in response.content
    assert LogEntry.objects.filter(
        object_repr="Delete safely", action_flag=DELETION
    ).exists()
