import pytest
from django.contrib.admin.models import CHANGE, LogEntry
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


def test_history_delete_confirmation_and_success_message_are_styled(static_live_server):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    article = Article.objects.create(title="Safe deletion target", slug="safe-deletion-target")
    LogEntry.objects.log_actions(
        user.pk,
        Article.objects.filter(pk=article.pk),
        CHANGE,
        "Updated the headline",
        single_object=True,
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.set_default_timeout(5000)
        _sign_in(page, static_live_server.url)

        history_url = reverse("admin:catalog_article_history", args=[article.pk])
        page.goto(f"{static_live_server.url}{history_url}")
        assert "Updated the headline" in page.locator("#change-history").inner_text()
        assert "newadmin-object-history" in page.locator("body").get_attribute("class")

        page.locator("html").evaluate("element => element.setAttribute('data-theme', 'light')")
        history_surface = page.locator("#change-history").evaluate(
            "element => getComputedStyle(element).backgroundColor"
        )
        assert history_surface == "rgb(255, 255, 255)"

        delete_url = reverse("admin:catalog_article_delete", args=[article.pk])
        page.goto(f"{static_live_server.url}{delete_url}")
        submit = page.locator('body.delete-confirmation input[type="submit"]')
        page.mouse.move(0, 0)
        page.locator("html").evaluate("element => element.setAttribute('data-theme', 'dark')")
        page.wait_for_function(
            "() => getComputedStyle(document.querySelector("
            "'body.delete-confirmation input[type=submit]')).backgroundColor "
            "=== 'rgb(255, 180, 168)'"
        )
        assert submit.evaluate("element => getComputedStyle(element).backgroundColor") == (
            "rgb(255, 180, 168)"
        )
        assert page.locator(
            '#content form input[name="csrfmiddlewaretoken"]'
        ).count() == 1

        page.get_by_role("button", name="Yes, I’m sure").click()
        success_message = page.locator(".messagelist li.success")
        assert success_message.count() == 1
        assert success_message.evaluate("element => getComputedStyle(element).borderRadius") == (
            "6px"
        )
        browser.close()

    assert not Article.objects.filter(pk=article.pk).exists()


def test_password_change_preserves_session_and_logout_submits_post(static_live_server):
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.set_default_timeout(5000)
        _sign_in(page, static_live_server.url)
        page.goto(f"{static_live_server.url}{reverse('admin:password_change')}")
        assert "newadmin-change-form" in page.locator("body").get_attribute("class")

        page.locator("#id_old_password").fill("secret")
        page.locator("#id_new_password1").fill("A-new-safe-password-2026")
        page.locator("#id_new_password2").fill("A-new-safe-password-2026")
        page.locator('input[type="submit"]').click()
        assert "Your password was changed." in page.locator("#content").inner_text()
        assert page.locator("#logout-form input[name=csrfmiddlewaretoken]").count() == 1

        with page.expect_response(
            lambda response: response.url.endswith(reverse("admin:logout"))
        ) as logout_response:
            page.locator("#logout-form button[type=submit]").click()

        assert logout_response.value.request.method == "POST"
        page.goto(f"{static_live_server.url}{reverse('admin:index')}")
        assert page.url.split("?", maxsplit=1)[0].endswith(reverse("admin:login"))
        browser.close()


def test_bulk_delete_confirmation_uses_newadmin_styles(static_live_server):
    get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    articles = [
        Article.objects.create(title=f"Bulk target {index}", slug=f"bulk-target-{index}")
        for index in range(2)
    ]

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.set_default_timeout(5000)
        _sign_in(page, static_live_server.url)
        page.goto(f"{static_live_server.url}{reverse('admin:catalog_article_changelist')}")

        page.locator("#action-toggle").check()
        page.locator("select[name=action]").select_option("delete_selected")
        page.locator('#changelist-form button[name="index"]').click()

        assert "delete-selected-confirmation" in page.locator("body").get_attribute("class")
        confirmation = page.locator("#content")
        for article in articles:
            assert article.title in confirmation.inner_text()
        assert confirmation.locator('form input[name="csrfmiddlewaretoken"]').count() == 1

        page.locator("html").evaluate("element => element.setAttribute('data-theme', 'dark')")
        page.wait_for_function(
            "() => getComputedStyle(document.querySelector("
            "'body.delete-selected-confirmation input[type=submit]')).backgroundColor "
            "=== 'rgb(255, 180, 168)'"
        )
        page.locator('input[type="submit"][value="Yes, I’m sure"]').click()
        browser.close()

    assert not Article.objects.filter(pk__in=[article.pk for article in articles]).exists()
