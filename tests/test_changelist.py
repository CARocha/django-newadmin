import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse

from demo.catalog.models import Article, Category

pytestmark = pytest.mark.django_db


def test_changelist_wraps_native_results_in_accessible_scroll_region(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)
    Article.objects.create(title="A thoughtful launch", slug="thoughtful-launch")

    response = client.get(reverse("admin:catalog_article_changelist"))

    assert response.status_code == 200
    assert b'class="newadmin-table-scroll"' in response.content
    assert b'role="region"' in response.content
    assert b'tabindex="0"' in response.content
    assert b'id="result_list"' in response.content


def test_filters_keep_native_details_state_and_gain_newadmin_class(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)
    category = Category.objects.create(name="News", slug="news")
    Article.objects.create(title="Release", slug="release", category=category)

    response = client.get(reverse("admin:catalog_article_changelist"))

    assert response.status_code == 200
    assert b'class="newadmin-filter"' in response.content
    assert b'data-filter-title="status"' in response.content
    assert b"<details" in response.content
    assert b'href="?category__id__exact=' in response.content


def test_read_only_staff_cannot_run_delete_selected(client):
    user = get_user_model().objects.create_user("reader", "reader@example.com", "secret")
    user.is_staff = True
    user.save(update_fields=["is_staff"])
    permission = Permission.objects.get(codename="view_article")
    user.user_permissions.add(permission)
    client.force_login(user)

    response = client.get(reverse("admin:catalog_article_changelist"))

    assert response.status_code == 200
    assert b'value="delete_selected"' not in response.content


def test_changelist_preserves_search_sorting_and_pagination(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)
    Article.objects.create(title="Match one", slug="match-one")
    Article.objects.create(title="Match two", slug="match-two")
    Article.objects.create(title="Other", slug="other")

    response = client.get(
        reverse("admin:catalog_article_changelist"),
        {"q": "Match", "o": "1"},
    )

    assert response.status_code == 200
    assert b"Match one" in response.content
    assert b"Match two" in response.content
    assert b"Other" not in response.content
    assert response.context["cl"].query == "Match"
    assert response.context["cl"].page_num == 1
    assert [article.title for article in response.context["cl"].result_list] == [
        "Match one",
        "Match two",
    ]


def test_changelist_shows_the_remaining_objects_on_the_next_page(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)
    Article.objects.bulk_create(
        [Article(title=f"Article {index:02}", slug=f"article-{index:02}") for index in range(25)]
    )

    response = client.get(reverse("admin:catalog_article_changelist"), {"p": 2})

    assert response.status_code == 200
    assert len(response.context["cl"].result_list) == 5


def test_empty_changelist_renders_without_a_results_table(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)

    response = client.get(reverse("admin:catalog_article_changelist"))

    assert response.status_code == 200
    assert b'class="newadmin-table-scroll"' in response.content
    assert b'id="result_list"' not in response.content
    assert response.context["cl"].result_count == 0


def test_invalid_list_editable_value_keeps_native_error_feedback(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)
    article = Article.objects.create(title="A draft", slug="a-draft")

    response = client.post(
        reverse("admin:catalog_article_changelist"),
        {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "1",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-id": str(article.pk),
            "form-0-title": article.title,
            "form-0-category": "",
            "form-0-status": "invalid",
            "_save": "Save",
        },
    )

    assert response.status_code == 200
    assert b"Select a valid choice" in response.content
    assert b"newadmin-table-scroll" in response.content
    article.refresh_from_db()
    assert article.status == Article.Status.DRAFT
