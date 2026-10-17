import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from playwright.sync_api import expect, sync_playwright

from demo.catalog.models import Article

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


def _sign_in(page, base_url):
    page.goto(f"{base_url}{reverse('admin:login')}")
    page.locator("#id_username").fill("editor")
    page.locator("#id_password").fill("secret")
    page.locator("input[type=submit]").click()


def test_date_time_file_and_textarea_widgets_keep_native_media(
    static_live_server, settings, tmp_path
):
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    article = Article.objects.create(title="Widget sample", slug="widget-sample")
    settings.MEDIA_ROOT = tmp_path / "media"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1100, "height": 900})
        page.set_default_timeout(5000)
        _sign_in(page, static_live_server.url)
        page.goto(
            f"{static_live_server.url}{reverse('admin:catalog_article_change', args=[article.pk])}"
        )

        assert page.locator('script[src*="admin/js/calendar.js"]').count() == 1
        assert page.locator('script[src*="admin/js/admin/DateTimeShortcuts.js"]').count() == 1
        assert page.locator('script[src*="/vendor/jquery/"]').count() == 1

        publication = page.locator("fieldset.module").filter(has_text="Publication")
        publication.locator("summary").click()
        date = page.locator("#id_published_at_0")
        time = page.locator("#id_published_at_1")
        expect(date).to_be_visible()
        expect(time).to_be_visible()
        page.locator("html").evaluate("element => element.dataset.theme = 'light'")
        page.locator("#calendarlink0").click()
        expect(page.locator("#calendarbox0")).to_be_visible()
        assert (
            page.locator("#calendarbox0").evaluate(
                "element => getComputedStyle(element).backgroundColor"
            )
            == "rgb(255, 255, 255)"
        )
        page.locator("#calendarbox0 .calendar-cancel a").click()
        page.locator("html").evaluate("element => element.dataset.theme = 'dark'")
        page.locator("#clocklink0").click()
        expect(page.locator("#clockbox0")).to_be_visible()
        assert (
            page.locator("#clockbox0").evaluate(
                "element => getComputedStyle(element).backgroundColor"
            )
            == "rgb(29, 39, 52)"
        )
        page.locator("#clockbox0 .calendar-cancel a").click()
        date.fill("2026-05-06")
        time.fill("14:30:00")

        upload = page.locator("#id_attachment")
        upload.set_input_files(
            {"name": "cover.txt", "mimeType": "text/plain", "buffer": b"AdminWP upload"}
        )
        textarea = page.locator("#id_body")
        textarea.fill("Widget body content")
        assert textarea.evaluate("element => getComputedStyle(element).borderRadius") == "4px"

        page.set_viewport_size({"width": 320, "height": 900})
        assert page.evaluate("document.documentElement.scrollWidth") <= 320
        page.locator('#article_form input[name="_save"]').click()
        page.goto(
            f"{static_live_server.url}{reverse('admin:catalog_article_change', args=[article.pk])}"
        )
        expect(page.locator("p.file-upload a")).to_have_text("articles/cover.txt")
        expect(page.locator("p.file-upload input[type=checkbox]")).to_be_visible()
        browser.close()

    article.refresh_from_db()
    assert timezone.localtime(article.published_at).strftime("%Y-%m-%d %H:%M:%S") == (
        "2026-05-06 14:30:00"
    )
    assert article.attachment.name.endswith("cover.txt")
    with article.attachment.open() as attachment:
        assert attachment.read() == b"AdminWP upload"
