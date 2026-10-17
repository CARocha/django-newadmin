import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from playwright.sync_api import sync_playwright

from demo.catalog.models import Article

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


def test_changelist_scrolls_searches_paginates_and_saves_inline_edits(static_live_server):
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    articles = [
        Article(
            title=f"Article {index:02}" + ("x" * 170 if index == 24 else ""),
            slug=f"article-{index:02}",
        )
        for index in range(25)
    ]
    Article.objects.bulk_create(articles)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 320, "height": 900})
        page.set_default_timeout(5000)
        page.goto(f"{static_live_server.url}{reverse('admin:login')}")
        page.locator("#id_username").fill("editor")
        page.locator("#id_password").fill("secret")
        page.locator("input[type=submit]").click()
        page.goto(f"{static_live_server.url}{reverse('admin:catalog_article_changelist')}")

        results_region = page.get_by_role("region", name="Scrollable articles results")
        results_region.wait_for()
        widths = results_region.evaluate(
            "element => ({content: element.clientWidth, table: element.scrollWidth, "
            "document: document.documentElement.scrollWidth})"
        )
        assert widths["table"] > widths["content"], widths
        assert widths["document"] <= 320

        page.locator("#searchbar").fill("Article 24")
        page.locator("#changelist-search input[type=submit]").click()
        assert page.locator("#result_list tbody tr").count() == 1
        assert "Article 24" in page.locator("#result_list").inner_text()
        title_cell = page.locator("#result_list tbody tr").first.locator("td").nth(1)
        assert title_cell.evaluate(
            "element => element.scrollWidth <= element.clientWidth"
        )

        page.goto(f"{static_live_server.url}{reverse('admin:catalog_article_changelist')}?p=2")
        assert page.locator("#result_list tbody tr").count() == 5

        page.goto(f"{static_live_server.url}{reverse('admin:catalog_article_changelist')}")
        page.get_by_role("button", name="Title", exact=True).click()
        assert page.locator("#result_list tbody tr").count() == 20

        row = page.locator("#result_list tbody tr").first
        article_id = page.locator('input[name$="-id"]').first.input_value()
        row.locator('select[name$="-status"]').select_option("published")
        page.locator('#changelist-form input[name="_save"]').click()
        browser.close()

    assert Article.objects.get(pk=article_id).status == Article.Status.PUBLISHED
