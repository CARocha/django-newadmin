import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from demo.catalog.models import Article

pytestmark = pytest.mark.django_db


def test_admin_lists_and_creates_articles(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)

    changelist = client.get(reverse("admin:catalog_article_changelist"))
    assert changelist.status_code == 200
    assert b"Articles" in changelist.content

    response = client.post(
        reverse("admin:catalog_article_add"),
        {
            "title": "A thoughtful launch",
            "slug": "thoughtful-launch",
            "category": "",
            "excerpt": "A demo article.",
            "body": "The content remains managed by Django.",
            "status": Article.Status.PUBLISHED,
            "_save": "Save",
        },
    )
    assert response.status_code == 302
    assert Article.objects.get(slug="thoughtful-launch").status == Article.Status.PUBLISHED


def test_admin_edits_and_deletes_articles(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)
    article = Article.objects.create(title="Draft", slug="draft", body="Initial")

    change_url = reverse("admin:catalog_article_change", args=[article.pk])
    response = client.post(
        change_url,
        {
            "title": "Updated draft",
            "slug": "updated-draft",
            "category": "",
            "excerpt": "",
            "body": "Updated content",
            "status": Article.Status.DRAFT,
            "_save": "Save",
        },
    )
    assert response.status_code == 302
    article.refresh_from_db()
    assert article.title == "Updated draft"

    delete_url = reverse("admin:catalog_article_delete", args=[article.pk])
    response = client.post(delete_url, {"post": "yes"})
    assert response.status_code == 302
    assert not Article.objects.filter(pk=article.pk).exists()
