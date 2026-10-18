"""Settings for the local NewAdmin demonstration."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
SECRET_KEY = "newadmin-demo-only-change-before-deployment"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
ROOT_URLCONF = "demo.config.urls"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "demo" / "media"

INSTALLED_APPS = [
    "newadmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "demo.catalog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

NEWADMIN = {
    "SITE_HEADER": "NewAdmin",
    "SITE_TITLE": "NewAdmin",
    "DASHBOARD": "demo.catalog.dashboard.EditorialDashboard",
    "MENU": {
        "ORDER": ["catalog", "auth"],
        "ICONS": {
            "catalog": "folder",
            "catalog.article": "file-text",
            "catalog.category": "tag",
            "auth": "users",
            "auth.user": "users",
            "auth.group": "users",
        },
    },
}
