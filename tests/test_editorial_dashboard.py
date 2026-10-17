import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from demo.catalog.dashboard import EditorialDashboard
from demo.catalog.models import Article, Category

pytestmark = pytest.mark.django_db


def test_editorial_dashboard_uses_real_counts_and_related_categories(django_assert_num_queries):
    category = Category.objects.create(name="News", slug="news")
    Article.objects.create(
        title="Published", slug="published", status="published", category=category
    )
    Article.objects.create(title="Draft", slug="draft", category=category)
    Article.objects.create(title="Uncategorized", slug="uncategorized")
    request = RequestFactory().get("/admin/")
    request.current_app = "admin"
    request.user = get_user_model().objects.create_superuser(
        "editor", "editor@example.com", "secret"
    )

    with django_assert_num_queries(4):
        data = EditorialDashboard().get_context_data(request)

    assert data["total"] == 3
    assert data["metrics"][0]["value"] == 1
    assert data["metrics"][1]["value"] == 2
    assert data["category_chart"]["rows"] == [["News", 2], ["Uncategorized", 1]]
    assert len(data["latest"]) == 3
    assert sum(row[1] for row in data["metrics"][0]["chart"]["rows"]) == 1
    assert sum(row[1] for row in data["metrics"][1]["chart"]["rows"]) == 2

    Article.objects.filter(status="draft").update(status="published")
    updated = EditorialDashboard().get_context_data(request)
    assert updated["metrics"][0]["value"] == 3
    assert updated["metrics"][1]["value"] == 0


def test_editorial_dashboard_keeps_an_empty_state_and_bounds_recent_entries():
    request = RequestFactory().get("/admin/")
    request.current_app = "admin"
    request.user = get_user_model().objects.create_superuser(
        "editor", "editor@example.com", "secret"
    )
    data = EditorialDashboard().get_context_data(request)

    assert data["total"] == 0
    assert data["category_chart"]["rows"] == []
    assert data["latest"] == []

    Article.objects.bulk_create([Article(title=f"Entry {n}", slug=f"entry-{n}") for n in range(12)])
    assert len(EditorialDashboard().get_context_data(request)["latest"]) == 8
