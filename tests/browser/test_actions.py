from urllib.parse import parse_qs, urlparse

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from playwright.sync_api import sync_playwright

from demo.catalog.models import Article, Category

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


def test_combined_filters_and_search_preserve_params_and_select_all_for_action(static_live_server):
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    news = Category.objects.create(name="News", slug="news")
    drafts = Category.objects.create(name="Drafts", slug="drafts")
    Article.objects.bulk_create(
        [
            Article(
                title=f"Release note {index:02}",
                slug=f"release-note-{index:02}",
                category=news,
                status=Article.Status.PUBLISHED,
            )
            for index in range(25)
        ]
        + [
            Article(
                title=f"Internal draft {index:02}",
                slug=f"internal-draft-{index:02}",
                category=drafts,
            )
            for index in range(5)
        ]
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.set_default_timeout(5000)
        page.goto(f"{static_live_server.url}{reverse('admin:login')}")
        page.locator("#id_username").fill("editor")
        page.locator("#id_password").fill("secret")
        page.locator("input[type=submit]").click()
        page.goto(f"{static_live_server.url}{reverse('admin:catalog_article_changelist')}")

        filters = page.locator("#changelist-filter")
        assert page.locator("#changelist-filter details.adminwp-filter").count() == 2
        filters.get_by_role("link", name="Show counts").click()
        assert "_facets" in parse_qs(urlparse(page.url).query)
        filters.get_by_role("link", name="Published (25)", exact=True).click()
        filters.get_by_role("link", name="News (25)", exact=True).click()
        page.set_viewport_size({"width": 320, "height": 900})
        page.locator("#searchbar").fill("Release")
        page.locator("#changelist-search input[type=submit]").click()

        params = parse_qs(urlparse(page.url).query)
        assert params["q"] == ["Release"]
        assert any(key.startswith("status") for key in params)
        assert any(key.startswith("category") for key in params)
        assert page.locator("#result_list tbody tr").count() == 20
        assert page.locator("#changelist-filter li.selected").count() >= 2
        overflowing = page.evaluate(
            "[...document.querySelectorAll('*')].filter(element => "
            "element.getBoundingClientRect().right > innerWidth).map(element => ({"
            "tag: element.tagName, id: element.id, className: element.className, "
            "right: element.getBoundingClientRect().right})).slice(0, 12)"
        )
        assert page.evaluate("document.documentElement.scrollWidth") <= 320, overflowing

        page.locator("#action-toggle").check()
        page.get_by_role("button", name="Select all 25 articles").click()
        page.locator("select[name=action]").select_option("delete_selected")
        page.locator('#changelist-form button[name="index"]').click()
        page.locator('input[type="submit"][value="Yes, I’m sure"]').click()
        browser.close()

    assert Article.objects.filter(category=news).count() == 0
    assert Article.objects.filter(category=drafts).count() == 5
