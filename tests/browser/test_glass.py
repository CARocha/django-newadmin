"""The optional blur must give way to opaque, readable surfaces on request."""

import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import expect, sync_playwright

from demo.catalog.models import Article, Category

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_glass_preserves_solid_content_and_respects_reduced_transparency(
    static_live_server, settings, tmp_path, mode
):
    settings.ADMINWP = {
        "SITE_HEADER": "AdminWP",
        "DASHBOARD": "demo.catalog.dashboard.EditorialDashboard",
    }
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    categories = [
        Category.objects.create(name=name, slug=name.lower()) for name in ("Design", "News")
    ]
    for index in range(6):
        Article.objects.create(
            title=f"Editorial story {index + 1}",
            slug=f"editorial-{index}",
            category=categories[index % 2],
            status="published" if index < 4 else "draft",
        )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(
            viewport={"width": 1440, "height": 1000}, color_scheme=mode, reduced_motion="reduce"
        )
        page.add_init_script(f"localStorage.setItem('theme', '{mode}')")
        page.goto(f"{static_live_server.url}/admin/login/")
        page.locator("#id_username").fill("editor")
        page.locator("#id_password").fill("secret")
        page.locator("input[type=submit]").click()
        page.locator("#editorial-categories svg").wait_for()
        blur = "el => getComputedStyle(el).backdropFilter"
        assert page.locator("#header").evaluate(blur) != "none"
        assert page.locator(".adminwp-panel").first.evaluate(blur) == "none"
        page.screenshot(path=str(tmp_path / f"glass-dashboard-{mode}.png"), full_page=True)
        page.goto(f"{static_live_server.url}/admin/catalog/article/add/")
        assert page.locator(".submit-row").evaluate(blur) != "none"
        assert page.locator("fieldset.module").first.evaluate(blur) == "none"
        assert page.locator("#id_title").evaluate("el => getComputedStyle(el).backgroundColor") == (
            "rgb(255, 255, 255)" if mode == "light" else "rgb(29, 39, 52)"
        )
        page.screenshot(path=str(tmp_path / f"glass-form-{mode}.png"), full_page=False)
        page.set_viewport_size({"width": 320, "height": 900})
        page.wait_for_function("document.documentElement.scrollWidth <= 320")
        page.screenshot(path=str(tmp_path / f"glass-mobile-{mode}.png"), full_page=True)

        session = page.context.new_cdp_session(page)
        session.send(
            "Emulation.setEmulatedMedia",
            {"features": [{"name": "prefers-reduced-transparency", "value": "reduce"}]},
        )
        page.wait_for_function("matchMedia('(prefers-reduced-transparency: reduce)').matches")
        for selector in ("#header", ".submit-row"):
            expect(page.locator(selector)).to_have_css("backdrop-filter", "none")
            assert page.locator(selector).evaluate(
                "el => getComputedStyle(el).backgroundColor"
            ) == ("rgb(255, 255, 255)" if mode == "light" else "rgb(29, 39, 52)")
        assert page.locator("body").evaluate("el => getComputedStyle(el).backgroundImage") == "none"
        browser.close()
