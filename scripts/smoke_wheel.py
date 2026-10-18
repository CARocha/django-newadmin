"""Run with a clean venv that has installed the built wheel, never editable."""

import re
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import django
from django.conf import settings

import newadmin

assert Path(newadmin.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()), (
    "Install the wheel into a clean virtual environment before running this smoke test."
)

with TemporaryDirectory(prefix="newadmin-wheel-") as temporary:
    settings.configure(
        SECRET_KEY="isolated-wheel-smoke-only",
        DEBUG=False,
        ALLOWED_HOSTS=["testserver"],
        ROOT_URLCONF=__name__,
        INSTALLED_APPS=[
            "newadmin",
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ]
                },
            }
        ],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        STATIC_URL="/static/",
        STATIC_ROOT=Path(temporary) / "static",
        STORAGES={
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
            }
        },
    )
    django.setup()
    from django.contrib import admin
    from django.contrib.auth import get_user_model
    from django.contrib.staticfiles.storage import staticfiles_storage
    from django.core.management import call_command
    from django.test import Client
    from django.urls import path

    urlpatterns = [path("admin/", admin.site.urls)]
    call_command("migrate", verbosity=0)
    call_command("collectstatic", interactive=False, verbosity=0)
    client = Client()
    assert client.get("/admin/login/").status_code == 200
    client.force_login(get_user_model().objects.create_superuser("smoke", password="local-only"))
    for route in ["/admin/", "/admin/auth/user/", "/admin/auth/user/add/"]:
        response = client.get(route)
        assert response.status_code == 200, route
        html = response.content.decode()
        assert "newadmin-theme" in html, route
        for url in re.findall(r'(?:src|href)="(/static/[^"#?]+)', html):
            assert staticfiles_storage.exists(url.removeprefix("/static/")), url
    for resource in [
        "icons.svg",
        "js/navigation.js",
        "js/accessibility.js",
        "vendor/echarts/echarts.min.js",
        "vendor/bootstrap-icons/LICENSE",
        "vendor/django/LICENSE",
        "vendor/bootstrap/LICENSE",
    ]:
        assert staticfiles_storage.exists(staticfiles_storage.stored_name("newadmin/" + resource))
    print(
        f"Installed wheel {newadmin.__version__}: Django {django.get_version()}, "
        "login/CRUD templates and manifest resources OK"
    )
