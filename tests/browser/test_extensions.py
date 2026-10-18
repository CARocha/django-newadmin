import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import expect, sync_playwright

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


def test_menu_icons_filter_and_links_use_the_active_site(static_live_server, settings, tmp_path):
    settings.NEWADMIN = {
        "SITE_HEADER": "NewAdmin",
        "MENU": {
            "ICONS": {"catalog.article": "file-text"},
            "LINKS": [
                {
                    "LABEL": "Editorial reports",
                    "URL_NAME": "admin:catalog_article_changelist",
                    "ICON": "chart",
                    "PERMISSIONS": ["catalog.view_article"],
                }
            ],
        },
        "SITES": {"operations": {"SITE_HEADER": "Operations"}},
    }
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(f"{static_live_server.url}/admin/login/")
        page.locator("#id_username").fill("editor")
        page.locator("#id_password").fill("secret")
        page.locator("input[type=submit]").click()
        sidebar = page.locator("#nav-sidebar")
        icon = sidebar.locator("#catalog-article .newadmin-icon")
        assert icon.get_attribute("aria-hidden") == "true"
        assert icon.locator("use").get_attribute("href").endswith("icons.svg#file-text")
        assert icon.evaluate("el => getComputedStyle(el).width") == "16px"
        # Django's native filter reads model-link innerHTML: SVG metadata must not match.
        page.locator("#nav-filter").fill("file-text")
        assert sidebar.locator("tr[class*=model-]:visible").count() == 0
        page.locator("#nav-filter").fill("Articles")
        assert sidebar.locator("tr[class*=model-]:visible").count() == 1
        page.locator("#nav-filter").press("Escape")
        expect(page.locator("#nav-filter")).to_have_value("")
        page.screenshot(path=str(tmp_path / "extensions-light.png"), full_page=True)
        page.goto(f"{static_live_server.url}/operations/")
        expect(page.locator("#site-name")).to_have_text("Operations")
        link = page.get_by_role("link", name="Editorial reports", exact=True)
        expect(link).to_have_attribute("href", "/operations/catalog/article/")
        link.click()
        expect(link).to_have_attribute("aria-current", "page")
        page.locator(".theme-toggle").click()
        # Native admin links animate colors: capture the settled dark palette.
        expect(link).to_have_css("color", "rgb(234, 240, 248)")
        expect(link).to_have_css("background-color", "rgb(29, 39, 52)")
        page.screenshot(path=str(tmp_path / "extensions-dark.png"), full_page=True)
        browser.close()
