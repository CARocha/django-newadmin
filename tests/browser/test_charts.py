import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import sync_playwright

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


def _sign_in(page, url):
    page.goto(f"{url}/admin/login/")
    page.locator("#id_username").fill("editor")
    page.locator("#id_password").fill("secret")
    page.locator("input[type=submit]").click()


def test_local_echarts_renders_two_charts_and_preserves_legend_selection_across_modes(
    static_live_server, settings
):
    settings.ADMINWP = {"DASHBOARD": "tests.dashboard_fixtures.ChartDashboard"}
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.set_default_timeout(5000)
        errors, requests = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: requests.append(request.url))
        _sign_in(page, static_live_server.url)

        page.locator("#category-counts svg").wait_for()
        page.locator("#secondary-chart svg").wait_for()
        assert page.evaluate("window.chartInjection") is None
        assert page.locator("#content img").count() == 0
        page.evaluate(
            "echarts.getInstanceByDom(document.getElementById('category-counts'))"
            ".dispatchAction({type: 'legendUnSelect', name: 'Drafts'})"
        )
        assert page.evaluate(
            "echarts.getInstanceByDom(document.getElementById('category-counts'))"
            ".getOption().legend[0].selected.Drafts"
        ) is False
        page.locator(".theme-toggle").click()
        page.wait_for_function("document.documentElement.dataset.bsTheme === 'dark'")
        page.wait_for_function(
            "echarts.getInstanceByDom(document.getElementById('category-counts'))"
            ".getModel().get('darkMode') === true"
        )
        assert page.evaluate(
            "echarts.getInstanceByDom(document.getElementById('category-counts'))"
            ".getOption().legend[0].selected.Drafts"
        ) is False
        page.set_viewport_size({"width": 320, "height": 900})
        page.wait_for_function("document.querySelector('#category-counts svg').clientWidth < 320")
        assert page.evaluate("document.documentElement.scrollWidth") <= 320, page.evaluate(
            "[...document.querySelectorAll('body *')].map(el => ({tag: el.tagName, "
            "class: el.className, right: el.getBoundingClientRect().right}))"
            ".filter(el => el.right > 320).slice(0, 12)"
        )
        assert errors == []
        assert all(url.startswith(static_live_server.url) for url in requests)
        browser.close()


def test_chart_data_remains_available_without_javascript(static_live_server, settings):
    settings.ADMINWP = {"DASHBOARD": "tests.dashboard_fixtures.ChartDashboard"}
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(java_script_enabled=False)
        page.set_default_timeout(5000)
        _sign_in(page, static_live_server.url)
        page.locator(".adminwp-chart__data summary").first.click()
        table = page.locator(".adminwp-chart__data table").first
        assert table.is_visible()
        assert "News" in table.inner_text()
        assert table.locator("tbody tr").count() == 2
        browser.close()
