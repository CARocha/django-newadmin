import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from playwright.sync_api import sync_playwright

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


def test_dashboard_has_contrasting_navigation_and_responsive_cards(static_live_server, tmp_path):
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.set_default_timeout(5000)
        page.goto(f"{static_live_server.url}{reverse('admin:login')}")
        page.locator("#id_username").fill("editor")
        page.locator("#id_password").fill("secret")
        page.locator("input[type=submit]").click()
        page.goto(f"{static_live_server.url}{reverse('admin:index')}")

        module = page.locator("#nav-sidebar .module").first
        module_background = module.evaluate("element => getComputedStyle(element).backgroundColor")
        row_background = module.locator("tr").first.evaluate(
            "element => getComputedStyle(element).backgroundColor"
        )
        module_link_color = module.locator(".section").evaluate(
            "element => getComputedStyle(element).color"
        )
        assert module_background == "rgba(0, 0, 0, 0)"
        assert row_background == "rgba(0, 0, 0, 0)"
        assert module_link_color == "rgb(83, 97, 114)"
        assert page.locator("#content-title").count() == 0
        assert page.locator(".newadmin-dashboard__card").count() >= 1
        assert page.locator(".newadmin-dashboard__activity").count() == 1
        page.screenshot(path=str(tmp_path / "dashboard-desktop.png"), full_page=True)

        page.locator("html").evaluate("element => element.setAttribute('data-theme', 'light')")
        light_surface = page.locator(".newadmin-dashboard__card").first.evaluate(
            "element => getComputedStyle(element).backgroundColor"
        )
        page.locator("html").evaluate("element => element.setAttribute('data-theme', 'dark')")
        dark_surface = page.locator(".newadmin-dashboard__card").first.evaluate(
            "element => getComputedStyle(element).backgroundColor"
        )
        assert dark_surface != light_surface

        page.set_viewport_size({"width": 320, "height": 900})
        assert page.evaluate("document.documentElement.scrollWidth") <= 320
        browser.close()
