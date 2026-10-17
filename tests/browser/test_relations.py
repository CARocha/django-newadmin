import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from demo.catalog.models import Article, Category

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


def _sign_in(page, base_url):
    page.goto(f"{base_url}{reverse('admin:login')}")
    page.locator("#id_username").fill("editor")
    page.locator("#id_password").fill("secret")
    page.locator("input[type=submit]").click()


def test_autocomplete_multiple_choice_and_inline_raw_id_popup(static_live_server):
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    technology = Category.objects.create(name="Technology", slug="technology")
    science = Category.objects.create(name="Science", slug="science")
    article = Article.objects.create(title="Relations", slug="relations")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 1000})
        page.set_default_timeout(5000)
        _sign_in(page, static_live_server.url)
        page.goto(
            f"{static_live_server.url}{reverse('admin:catalog_article_change', args=[article.pk])}"
        )

        assert page.locator('script[src*="/vendor/jquery/"]').count() == 1
        category = page.locator("#id_category")
        assert category.evaluate("element => element.classList.contains('admin-autocomplete')")
        category_ui = page.locator("#id_category + span .select2-selection")
        category_ui.click()
        page.locator(".select2-search__field").fill("Tech")
        page.locator(".select2-results__option").filter(has_text="Technology").click()
        expect(category).to_have_value(str(technology.pk))
        assert category_ui.evaluate("element => getComputedStyle(element).borderRadius") == "8px"

        available_title = page.locator(".selector-available-title, .selector-available h2").first
        chosen_title = page.locator(".selector-chosen-title, .selector-chosen h2").first
        title_style = "el => [getComputedStyle(el).backgroundColor, getComputedStyle(el).color]"
        assert chosen_title.evaluate(title_style) == available_title.evaluate(title_style)
        assert page.locator("#id_topics_add").evaluate(
            "el => getComputedStyle(el).backgroundImage"
        ) != "none"

        page.locator("#id_topics_from").select_option(str(science.pk))
        page.locator("#id_topics_add").click()
        assert page.locator("#id_topics_to option").all_text_contents() == ["Science"]

        links = page.locator("#links-group")
        links.locator(".add-row a").click()
        page.locator("#id_links-0-label").fill("Related category")
        page.locator("#id_links-0-url").fill("https://example.com/category")
        with page.expect_popup() as popup_info:
            page.locator("#lookup_id_links-0-category").click()
        popup = popup_info.value
        popup.get_by_role("link", name="Science", exact=True).click()
        expect(page.locator("#id_links-0-category")).to_have_value(str(science.pk))
        assert popup.is_closed()

        selector = page.locator(".selector").first
        page.set_viewport_size({"width": 390, "height": 844})
        assert (
            len(
                selector.evaluate(
                    "element => getComputedStyle(element).gridTemplateColumns"
                ).split()
            )
            == 1
        )
        page.locator("html").evaluate("element => element.dataset.theme = 'dark'")
        assert (
            page.locator(".select2-container--admin-autocomplete .select2-selection").evaluate(
                "element => getComputedStyle(element).backgroundColor"
            )
            == "rgb(29, 39, 52)"
        )

        page.locator('#article_form input[name="_save"]').click()
        browser.close()

    article.refresh_from_db()
    assert article.category == technology
    assert list(article.topics.all()) == [science]
    link = article.links.get()
    assert link.category == science
