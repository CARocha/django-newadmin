import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.urls import reverse

from newadmin.dashboard import EChartsDashboard
from tests.dashboard_fixtures import ExampleDashboard

pytestmark = pytest.mark.django_db


@pytest.fixture
def dashboard_templates(settings, tmp_path):
    (tmp_path / "dashboard_probe.html").write_text(
        '{% extends "newadmin/dashboard/layout.html" %}'
        "{% block dashboard_primary %}<p>{{ dashboard_data.message }}</p>{% endblock %}"
    )
    settings.TEMPLATES = [
        {**settings.TEMPLATES[0], "DIRS": [tmp_path]},
    ]


@override_settings(NEWADMIN={"DASHBOARD": "tests.dashboard_fixtures.ExampleDashboard"})
def test_provider_renders_its_template_and_media_without_overwriting_native_context(
    client, dashboard_templates
):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)

    response = client.get(reverse("admin:index"))

    assert response.status_code == 200
    assert b"Panel for editor" in response.content
    assert b"Injected header" not in response.content
    assert response.content.count(b"dashboard-probe.js") == 1


@override_settings(NEWADMIN={"DASHBOARD": "tests.dashboard_fixtures.PrivateDashboard"})
def test_provider_checks_permissions_before_queries_or_media_are_evaluated(client):
    user = get_user_model().objects.create_user("reader", password="secret", is_staff=True)
    client.force_login(user)

    response = client.get(reverse("admin:index"))

    assert response.status_code == 200
    assert b"Recent actions" in response.content
    assert b"dashboard-probe.js" not in response.content


@override_settings(NEWADMIN={"DASHBOARD": "tests.dashboard_fixtures.ExampleDashboard"})
def test_provider_evaluates_once_per_request_and_never_shares_user_data(
    client, dashboard_templates, monkeypatch
):
    calls = []

    def context_data(self, request):
        calls.append(request.user.pk)
        return {"message": request.user.username}

    monkeypatch.setattr(ExampleDashboard, "get_context_data", context_data)
    first = get_user_model().objects.create_superuser("first", "first@example.com", "secret")
    second = get_user_model().objects.create_superuser("second", "second@example.com", "secret")
    for user in (first, second):
        client.force_login(user)
        response = client.get(reverse("admin:index"))
        assert user.username.encode() in response.content

    assert calls == [first.pk, second.pk]


@pytest.mark.parametrize(
    "provider",
    ["missing.Dashboard", "django.forms.Form", "tests.dashboard_fixtures.BrokenDashboard"],
)
def test_invalid_provider_configuration_has_an_identifiable_error(client, settings, provider):
    settings.NEWADMIN = {"DASHBOARD": provider}
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)

    with pytest.raises(ImproperlyConfigured, match="NEWADMIN.DASHBOARD"):
        client.get(reverse("admin:index"))


def test_echarts_provider_adds_only_local_chart_resources():
    media = str(EChartsDashboard().media)

    assert "newadmin/vendor/echarts/echarts.min.js" in media
    assert "newadmin/js/dashboard-charts.js" in media
    assert "https://" not in media


@override_settings(NEWADMIN={"DASHBOARD": "tests.dashboard_fixtures.ExampleDashboard"})
def test_business_dashboard_does_not_replace_app_index_or_model_pages(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)

    for url in (
        reverse("admin:app_list", args=["catalog"]),
        reverse("admin:catalog_article_changelist"),
    ):
        response = client.get(url)
        assert response.status_code == 200
        assert b"dashboard-probe.js" not in response.content


def test_default_dashboard_does_not_load_chart_javascript(client):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)

    assert b"echarts.min.js" not in client.get(reverse("admin:index")).content


@override_settings(
    ROOT_URLCONF="tests.dashboard_urls",
    NEWADMIN={
        "DASHBOARD": "tests.dashboard_fixtures.ExampleDashboard",
        "SITES": {"reports": {"DASHBOARD": None}},
    },
)
def test_provider_can_be_disabled_independently_for_another_admin_site(client, dashboard_templates):
    user = get_user_model().objects.create_superuser("editor", "editor@example.com", "secret")
    client.force_login(user)

    assert b"Panel for editor" in client.get(reverse("admin:index")).content
    report_page = client.get(reverse("reports:index"))
    assert b"Panel for editor" not in report_page.content
    assert b"Recent actions" in report_page.content
