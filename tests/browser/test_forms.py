import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from playwright.sync_api import sync_playwright

from demo.catalog.models import Article

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


def _sign_in(page, base_url):
    page.goto(f"{base_url}{reverse('admin:login')}")
    page.locator("#id_username").fill("editor")
    page.locator("#id_password").fill("secret")
    page.locator("input[type=submit]").click()


def test_add_form_keeps_native_fieldsets_help_and_validation(static_live_server):
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1100, "height": 900})
        page.set_default_timeout(5000)
        _sign_in(page, static_live_server.url)
        page.goto(f"{static_live_server.url}{reverse('admin:catalog_article_add')}")

        assert "adminwp-change-form" in page.locator("body").get_attribute("class")
        assert page.locator("form#article_form .form-row").count() >= 7
        assert page.locator("form#article_form .help").count() >= 1
        headings = page.locator("form#article_form fieldset.module h2").all_text_contents()
        assert headings == ["Story", "Publication", "Timestamps"]

        publication = page.locator("fieldset.module").filter(has_text="Publication")
        details = publication.locator("details")
        assert not details.evaluate("element => element.open")
        details.locator("summary").click()
        assert details.evaluate("element => element.open")

        page.locator("#id_slug").fill("valid-slug")
        page.locator('input[name="_save"]').click()
        assert page.locator("#id_title").count() == 1
        assert page.locator("#article_form .errorlist").count() >= 1
        assert page.locator("#article_form .errornote").count() == 1
        page.locator("html").evaluate("element => element.setAttribute('data-theme', 'light')")
        error_border = page.locator("#id_title").evaluate(
            "element => getComputedStyle(element).borderColor"
        )
        assert error_border == "rgb(180, 35, 24)"
        browser.close()


def test_edit_form_shows_readonly_timestamps_and_adapts_to_dark_mode(static_live_server):
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    article = Article.objects.create(title="Existing", slug="existing")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.set_default_timeout(5000)
        _sign_in(page, static_live_server.url)
        page.goto(
            f"{static_live_server.url}{reverse('admin:catalog_article_change', args=[article.pk])}"
        )

        readonly = page.locator("#article_form .readonly")
        assert readonly.count() == 2
        assert page.locator("#id_created_at").count() == 0
        assert page.locator("#id_updated_at").count() == 0

        page.set_viewport_size({"width": 320, "height": 900})
        assert page.evaluate("document.documentElement.scrollWidth") <= 320

        page.locator("html").evaluate("element => element.setAttribute('data-theme', 'dark')")
        dark_bg = page.locator("fieldset.module").first.evaluate(
            "element => getComputedStyle(element).backgroundColor"
        )
        page.locator("html").evaluate("element => element.setAttribute('data-theme', 'light')")
        light_bg = page.locator("fieldset.module").first.evaluate(
            "element => getComputedStyle(element).backgroundColor"
        )
        assert dark_bg != light_bg
        browser.close()
