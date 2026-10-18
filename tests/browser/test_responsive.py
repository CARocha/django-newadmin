import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import expect, sync_playwright

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("language", ["en", "ar"])
def test_navigation_reflows_and_is_keyboard_operable(
    static_live_server, settings, language, tmp_path
):
    settings.LANGUAGE_CODE = language
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 320, "height": 900}, reduced_motion="reduce")
        page.goto(static_live_server.url + "/admin/login/")
        page.locator("#id_username").fill("editor")
        page.locator("#id_password").fill("secret")
        page.locator("input[type=submit]").click()
        toggle = page.locator("#toggle-nav-sidebar")
        sidebar = page.locator("#nav-sidebar")
        expect(toggle).to_be_visible()
        expect(toggle).to_have_attribute("aria-controls", "nav-sidebar")
        expect(toggle).to_have_attribute("aria-expanded", "false")
        toggle.focus()
        page.keyboard.press("Enter")
        expect(toggle).to_have_attribute("aria-expanded", "true")
        expect(sidebar).not_to_have_attribute("inert", "")
        page.locator("#nav-filter").focus()
        page.keyboard.press("Escape")
        expect(toggle).to_be_focused()
        expect(toggle).to_have_attribute("aria-expanded", "false")
        expect(sidebar).to_have_attribute("inert", "")
        for width in (320, 768, 1024, 1440):
            page.set_viewport_size({"width": width, "height": 900})
            for route in ("/admin/", "/admin/catalog/article/", "/admin/catalog/article/add/"):
                page.goto(static_live_server.url + route)
                page.wait_for_function("document.documentElement.scrollWidth <= innerWidth")
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (
                    language,
                    width,
                    route,
                )
                if route.endswith("/add/"):
                    for selector in ("#id_title", "#id_slug", "#id_excerpt", "#id_body"):
                        bounds = page.locator(selector).evaluate("""el => {
                            const field = el.getBoundingClientRect();
                            const panel = el.closest('fieldset.module').getBoundingClientRect();
                            return {left:field.left, right:field.right,
                                panelLeft:panel.left, panelRight:panel.right};
                        }""")
                        assert bounds["left"] >= bounds["panelLeft"] + 1, (selector, bounds)
                        assert bounds["right"] <= bounds["panelRight"] - 1, (selector, bounds)
            if width == 320:
                page.screenshot(path=str(tmp_path / f"mobile-{language}.png"), full_page=True)
        # 1280 CSS pixels at 400% browser zoom reflow to a 320 CSS pixel viewport.
        page.set_viewport_size({"width": 320, "height": 700})
        page.goto(static_live_server.url + "/admin/catalog/article/")
        region = page.locator(".adminwp-table-scroll")
        if region.count():
            expect(region).to_have_attribute("tabindex", "0")
        browser.close()
