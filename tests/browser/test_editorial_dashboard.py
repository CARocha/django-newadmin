from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from playwright.sync_api import sync_playwright

from demo.catalog.models import Article, Category

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


def test_editorial_dashboard_matches_reference_proportions_and_both_modes(
    static_live_server, settings, tmp_path
):
    settings.NEWADMIN = {
        "SITE_HEADER": "NewAdmin",
        "DASHBOARD": "demo.catalog.dashboard.EditorialDashboard",
    }
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    for n, name in enumerate(["Technology", "Culture", "World", "Science", "Business"]):
        category = Category.objects.create(name=name, slug=name.lower())
        for index in range(5 - n):
            Article.objects.create(
                title=f"{name}: a closer look at the stories shaping our week {index + 1}",
                slug=f"{category.slug}-{index}",
                category=category,
                status="published" if index % 2 == 0 else "draft",
                created_at=timezone.now() - timedelta(days=(n + index) % 7),
            )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        page.set_default_timeout(5000)
        page.goto(f"{static_live_server.url}/admin/login/")
        page.locator("#id_username").fill("editor")
        page.locator("#id_password").fill("secret")
        page.locator("input[type=submit]").click()
        page.locator("#editorial-categories svg").wait_for()
        assert (
            page.locator(".newadmin-workspace__actions .btn-primary").evaluate(
                "el => getComputedStyle(el).color"
            )
            == "rgb(255, 255, 255)"
        )

        assert page.locator("#header").bounding_box()["height"] == 64
        sidebar_width = sum(
            page.locator(selector).bounding_box()["width"]
            for selector in ("#nav-sidebar", "#toggle-nav-sidebar")
        )
        assert sidebar_width == 256
        primary = page.locator(".newadmin-workspace__primary").bounding_box()
        metrics = page.locator(".newadmin-workspace__metrics").bounding_box()
        assert abs(primary["width"] / metrics["width"] - 2) < 0.01
        assert page.locator(".newadmin-metric").count() == 2
        assert page.locator(".newadmin-editorial-table tbody tr").count() == 8
        page.screenshot(
            path=str(tmp_path / "editorial-light.png"), full_page=True, animations="disabled"
        )

        page.locator(".theme-toggle").click()
        page.wait_for_function("document.documentElement.dataset.bsTheme === 'dark'")
        page.screenshot(
            path=str(tmp_path / "editorial-dark.png"), full_page=True, animations="disabled"
        )
        page.set_viewport_size({"width": 320, "height": 900})
        page.wait_for_function(
            "document.querySelector('#editorial-categories svg').clientWidth < 320"
        )
        assert page.locator(".newadmin-workspace__heading").bounding_box()["y"] >= (
            page.locator("#header").bounding_box()["y"]
            + page.locator("#header").bounding_box()["height"]
        )
        page.screenshot(
            path=str(tmp_path / "editorial-mobile.png"), full_page=True, animations="disabled"
        )
        assert page.evaluate("document.documentElement.scrollWidth") <= 320, page.evaluate(
            "[...document.querySelectorAll('body *')].filter(el => el instanceof HTMLElement)"
            ".map(el => ({tag: el.tagName, class: el.className, "
            "right: el.getBoundingClientRect().right}))"
            ".filter(el => el.right > 320).slice(0, 12)"
        )
        browser.close()
