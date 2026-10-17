from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import expect, sync_playwright

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]
AXE = Path(__file__).resolve().parents[2] / "node_modules/axe-core/axe.min.js"


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_core_pages_have_no_automated_wcag_aa_violations(static_live_server, mode):
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(reduced_motion="reduce")
        page.add_init_script(f"localStorage.setItem('theme', '{mode}')")
        page.goto(f"{static_live_server.url}/admin/login/")
        routes = [
            None,
            "/admin/",
            "/admin/catalog/article/",
            "/admin/catalog/article/add/",
            "/admin/password_change/",
        ]
        for route in routes:
            if route:
                page.goto(static_live_server.url + route)
            page.add_script_tag(path=str(AXE))
            result = page.evaluate("""async () => {
                const r = await axe.run(document, {runOnly: {type: 'tag',
                    values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']}});
                return r.violations.map(v => ({id:v.id, impact:v.impact,
                    nodes:v.nodes.map(n=>({target:n.target,
                        summary:n.failureSummary, html:n.html}))}));
            }""")
            assert result == [], (mode, route or "login", result)
            if route is None:
                page.locator("#id_username").fill("editor")
                page.locator("#id_password").fill("secret")
                page.locator("input[type=submit]").click()
        # First Tab follows the native skip link and Enter reaches the main landmark.
        page.goto(static_live_server.url + "/admin/")
        page.keyboard.press("Tab")
        expect(page.locator(".skip-to-content-link")).to_be_focused()
        page.keyboard.press("Enter")
        expect(page.locator("#content-start")).to_be_focused()
        browser.close()
