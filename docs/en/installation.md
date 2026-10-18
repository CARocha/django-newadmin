# Installation

## Requirements

- A virtual environment with Python 3.13 or 3.14.
- A project with Django 6.0 or 6.1 admin enabled.
- `django.contrib.staticfiles` and its usual static-file configuration.

## Install the package

Until the release is available, install the wheel supplied by the maintainer
(adjust the path):

```sh
python -m pip install /path/django_newadmin-0.1.0a1-py3-none-any.whl
```

After publication on PyPI, use:

```sh
python -m pip install 'django-newadmin==0.1.0a1'
```

Pinning the version selects this alpha explicitly. The package resolves Django
within its supported range. If Django is already installed, review pip's upgrade
plan before changing a production environment.

## Enable it in an existing project

In `settings.py`, place `newadmin` **before** `django.contrib.admin`:

```python
INSTALLED_APPS = [
    'newadmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Your applications...
]
```

Keep the `request`, `auth`, and `messages` context processors, the usual admin
middleware, and `APP_DIRS=True` (or the equivalent application loader). A project
created with `startproject` already includes this setup.

Do not change your `ModelAdmin` registrations or add theme middleware. The theme
has no migrations of its own. For a new project, apply **Django's** migrations
and create an administrator:

```sh
python manage.py migrate
python manage.py createsuperuser
python manage.py check
python manage.py runserver
```

Mount the admin in `urls.py`:

```python
from django.contrib import admin
from django.urls import path

urlpatterns = [path('admin/', admin.site.urls)]
```

Open `/admin/`. The theme styles login, dashboard, changelists, forms, widgets,
and auxiliary pages. `NEWADMIN` is optional:

```python
NEWADMIN = {'SITE_HEADER': 'My site', 'DEFAULT_MODE': 'auto'}
```

Continue with [configuration](configuration.md) and [dashboards](dashboard.md).

## Static files in production

Configure `STATIC_URL`, `STATIC_ROOT`, and static-file serving as you would for
Django. Here is an example using manifest storage:

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage',
    },
}
```

```sh
python manage.py collectstatic --noinput
```

Serve that directory with your static-file server; `runserver` is not a
production server. Do not replace the `default` storage if your project already
uses it for uploaded files. Keep your current static-files backend if it is
compatible with Django.

The wheel contains CSS, JavaScript, icons, and ECharts. Run `collectstatic` after
each update. `LOGO` and `CUSTOM_CSS` paths are resolved through staticfiles. With
a CDN on another origin, check external SVG loading and your deployment's CORS
policy; the initial test matrix covers same-origin resources.

## Disable or update

To disable the theme, remove `newadmin` from `INSTALLED_APPS` and remove consumer
overrides that depend on its templates. Django admin returns to its default
style. To update, install the desired version, review the changelog, rerun
`collectstatic`, and test your overrides, forms, and dashboards in staging.

## Local repository demo

From a project checkout:

```sh
python -m venv .venv
.venv/bin/python -m pip install -e '.[dev,docs]'
.venv/bin/python demo/manage.py migrate
.venv/bin/python demo/manage.py seed_demo
.venv/bin/python demo/manage.py createsuperuser
.venv/bin/python demo/manage.py runserver
```

The demo uses SQLite for local development. Theme users do not need to install
or copy `demo`.
