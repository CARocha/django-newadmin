import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from demo.catalog.models import Article, ArticleLink, ArticleSection

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


def _sign_in(page, base_url):
    page.goto(f"{base_url}{reverse('admin:login')}")
    page.locator("#id_username").fill("editor")
    page.locator("#id_password").fill("secret")
    page.locator("input[type=submit]").click()


def _open_article(page, base_url, article):
    _sign_in(page, base_url)
    page.goto(
        f"{base_url}{reverse('admin:catalog_article_change', args=[article.pk])}"
    )


def test_tabular_and_stacked_inlines_add_delete_and_save_rows(static_live_server):
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    article = Article.objects.create(title="Inline article", slug="inline-article")
    old_link = ArticleLink.objects.create(
        article=article, label="Old link", url="https://example.com/old"
    )
    old_section = ArticleSection.objects.create(
        article=article, heading="Existing section", body="Keep this section."
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 1000})
        page.set_default_timeout(5000)
        _open_article(page, static_live_server.url, article)

        links = page.locator("#links-group")
        assert links.locator(".tabular").count() == 1
        assert not links.locator("tr.empty-form").is_visible()
        links.locator(".add-row a").click()
        page.locator("#id_links-1-label").fill("New link")
        page.locator("#id_links-1-url").fill("https://example.com/new")
        page.locator("#id_links-0-DELETE").check()

        sections = page.locator("#sections-group")
        assert sections.get_attribute("data-inline-type") == "stacked"
        page.locator("#id_sections-0-heading").fill("Updated section")
        sections.locator(".add-row a").click()
        page.locator("#id_sections-1-heading").fill("New section")
        page.locator("#id_sections-1-body").fill("A new block of content.")

        page.locator("html").evaluate("element => element.setAttribute('data-theme', 'dark')")
        dark_header = links.locator("thead th").first.evaluate(
            "element => getComputedStyle(element).backgroundColor"
        )
        page.locator("html").evaluate("element => element.setAttribute('data-theme', 'light')")
        light_header = links.locator("thead th").first.evaluate(
            "element => getComputedStyle(element).backgroundColor"
        )
        assert dark_header != light_header

        page.set_viewport_size({"width": 320, "height": 900})
        wrapper = links.locator(".wrapper")
        table_widths = wrapper.evaluate(
            "element => ({client: element.clientWidth, scroll: element.scrollWidth, "
            "radius: getComputedStyle(element).borderRadius})"
        )
        assert table_widths["scroll"] > table_widths["client"]
        assert table_widths["radius"] == "8px"
        assert page.evaluate("document.documentElement.scrollWidth") <= 320
        page.set_viewport_size({"width": 1280, "height": 1000})
        page.locator('#article_form input[name="_save"]').click()
        browser.close()

    assert not ArticleLink.objects.filter(pk=old_link.pk).exists()
    assert list(article.links.values_list("label", flat=True)) == ["New link"]
    assert list(article.sections.values_list("heading", flat=True)) == [
        "Updated section",
        "New section",
    ]
    assert ArticleSection.objects.get(pk=old_section.pk).body == "Keep this section."


def test_inline_validation_can_be_fixed_and_saved(static_live_server):
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    article = Article.objects.create(title="Inline article", slug="inline-validation")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 1000})
        page.set_default_timeout(5000)
        _open_article(page, static_live_server.url, article)
        links = page.locator("#links-group")
        links.locator(".add-row a").click()
        page.locator("#id_links-0-url").fill("https://example.com/fixed")
        page.locator('#article_form input[name="_save"]').click()

        expect(page.locator("#links-0 .errorlist")).to_have_count(1)
        assert page.locator("#links-0 .errorlist").inner_text() == "This field is required."
        page.locator("#id_links-0-label").fill("Fixed link")
        page.locator('#article_form input[name="_save"]').click()
        browser.close()

    link = ArticleLink.objects.get(article=article)
    assert link.label == "Fixed link"
    assert link.url == "https://example.com/fixed"
