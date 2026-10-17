"""Catch a theme that is accidentally restricted to the dashboard again."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from playwright.sync_api import sync_playwright

from demo.catalog.models import Article

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("mode", ["light", "dark", "auto"])
def test_admin_pages_share_dashboard_shell_and_palette(static_live_server, mode, tmp_path):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    article = Article.objects.create(title="Shared appearance", slug="shared-appearance")
    routes = [
        reverse("admin:catalog_article_add"),
        reverse("admin:catalog_article_changelist"),
        reverse("admin:catalog_article_change", args=[article.pk]),
        reverse("admin:app_list", args=["catalog"]),
        reverse("admin:catalog_article_history", args=[article.pk]),
        reverse("admin:catalog_article_delete", args=[article.pk]),
        reverse("admin:password_change"),
        reverse("admin:auth_user_password_change", args=[user.pk]),
    ]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(
            viewport={"width": 1440, "height": 1000},
            color_scheme="dark" if mode == "auto" else mode,
            reduced_motion="reduce",
        )
        page.add_init_script(f"localStorage.setItem('theme', '{mode}')")
        page.goto(f"{static_live_server.url}{reverse('admin:login')}")
        assert page.locator("#container").bounding_box()["width"] < 600
        assert page.locator(".adminwp-header-context").count() == 0
        page.locator("#id_username").fill("editor")
        page.locator("#id_password").fill("secret")
        page.locator("input[type=submit]").click()
        read_palette = """() => {
            const style = getComputedStyle(document.body);
            return Object.fromEntries(['--adminwp-canvas', '--adminwp-surface',
                '--adminwp-primary', '--button-bg', '--header-bg', '--body-bg']
                .map(key => [key, style.getPropertyValue(key).trim()]));
        }"""
        dashboard_palette = page.evaluate(read_palette)
        header_background = page.locator("#header").evaluate(
            "el => getComputedStyle(el).backgroundColor"
        )
        sidebar_background = page.locator("#nav-sidebar").evaluate(
            "el => getComputedStyle(el).backgroundColor"
        )
        for index, route in enumerate(routes):
            page.goto(f"{static_live_server.url}{route}")
            assert page.evaluate(read_palette) == dashboard_palette, route
            heading = page.locator("#content > h1, #content .titles h1")
            if heading.count():
                assert heading.first.evaluate("el => getComputedStyle(el).fontSize") == "28px"
            if page.locator("body.change-form fieldset.module").count():
                assert (
                    page.locator("fieldset.module").first.evaluate(
                        "el => getComputedStyle(el).borderRadius"
                    )
                    == "4px"
                ), route
            assert page.locator("#header").bounding_box()["height"] == 64, route
            assert page.locator("#branding").bounding_box()["width"] == 256, route
            assert (
                page.locator("#header").evaluate("el => getComputedStyle(el).backgroundColor")
                == header_background
            ), route
            if page.locator("#nav-sidebar").count():
                assert (
                    sum(
                        page.locator(selector).bounding_box()["width"]
                        for selector in ("#nav-sidebar", "#toggle-nav-sidebar")
                    )
                    == 256
                ), route
                assert (
                    page.locator("#nav-sidebar").evaluate(
                        "el => getComputedStyle(el).backgroundColor"
                    )
                    == sidebar_background
                ), route
                assert page.locator('.adminwp-nav-home[aria-current="page"]').count() == 0
            if index < 2:
                page.screenshot(
                    path=str(tmp_path / f"{mode}-{index}-viewport.png"), full_page=False
                )
                page.screenshot(path=str(tmp_path / f"{mode}-{index}.png"), full_page=True)
            page.set_viewport_size({"width": 320, "height": 900})
            page.wait_for_function(
                "window.matchMedia('(max-width: 767px)').matches && "
                "getComputedStyle(document.querySelector('#container')).minWidth === '0px'"
            )
            assert page.evaluate("document.documentElement.scrollWidth") <= 320, (
                route,
                page.evaluate(
                    "[...document.querySelectorAll('body *')]"
                    ".filter(el => el instanceof HTMLElement)"
                    ".map(el => ({tag: el.tagName, id: el.id, cls: el.className, "
                    "right: el.getBoundingClientRect().right, "
                    "width: el.getBoundingClientRect().width}))"
                    ".filter(el => el.right > 320).slice(0, 18)"
                ),
            )
            assert page.locator("#content").bounding_box()["y"] >= (
                page.locator("#header").bounding_box()["y"]
                + page.locator("#header").bounding_box()["height"]
            ), route
            page.set_viewport_size({"width": 1440, "height": 1000})
        page.goto(f"{static_live_server.url}{routes[0]}?_popup=1")
        assert page.evaluate(read_palette) == dashboard_palette
        assert page.locator("#header, #nav-sidebar, #toggle-nav-sidebar").count() == 0
        page.wait_for_function("document.documentElement.scrollWidth <= innerWidth")
        page.screenshot(path=str(tmp_path / f"{mode}-popup.png"), full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth") <= 1440, page.evaluate(
            "[...document.querySelectorAll('body *')]"
            ".filter(el => el instanceof HTMLElement)"
            ".map(el => ({tag: el.tagName, id: el.id, cls: el.className, "
            "right: el.getBoundingClientRect().right}))"
            ".filter(el => el.right > 1440).slice(0, 18)"
        )
        browser.close()


def test_long_page_title_leaves_account_controls_inside_tablet_header(static_live_server):
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    target = get_user_model().objects.create_user("editor_" * 12)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1101, "height": 900})
        page.goto(f"{static_live_server.url}{reverse('admin:login')}")
        page.locator("#id_username").fill("editor")
        page.locator("#id_password").fill("secret")
        page.locator("input[type=submit]").click()
        page.goto(
            f"{static_live_server.url}"
            f"{reverse('admin:auth_user_password_change', args=[target.pk])}"
        )
        assert target.username in page.locator(".adminwp-header-context").inner_text()
        assert page.locator("#header").bounding_box()["height"] == 64
        toggle = page.locator("#user-tools .theme-toggle").bounding_box()
        assert toggle["x"] + toggle["width"] <= 1101
        assert page.evaluate("document.documentElement.scrollWidth") <= 1101
        browser.close()
