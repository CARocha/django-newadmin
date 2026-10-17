# django-adminwp

A WordPress-inspired, light-and-dark theme for Django's built-in admin.

**Status:** early development. The first target matrix (Django 6.0 and 6.1 on
Python 3.13 and 3.14) passes locally; automated CI has not been configured yet.

## Development setup

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest tests --ignore=tests/browser -q
.venv/bin/python -m playwright install chromium
.venv/bin/python -m pytest tests/browser -q
npm ci
npm run build:css
npm run build:charts
npm run test:js
```

The npm commands are for developing AdminWP's assets. Installing the Python
package includes the compiled files and does not require Node.js.

## Activate AdminWP

Add `adminwp` before Django's admin app. No model changes, middleware, or
migrations are required in a consuming project:

```python
INSTALLED_APPS = [
    "adminwp",
    "django.contrib.admin",
    # Other Django apps.
]
```

The theme works with its defaults. Optional site branding and appearance can be
set in `settings.py`:

```python
ADMINWP = {
    "SITE_TITLE": "Studio",
    "SITE_HEADER": "Studio control room",
    "DEFAULT_MODE": "auto",  # light, dark, or auto
}
```

## Run the demo

After installing the project in editable mode, prepare the sample catalog and
create a local administrator:

```sh
.venv/bin/python demo/manage.py migrate
.venv/bin/python demo/manage.py seed_demo
.venv/bin/python demo/manage.py createsuperuser
.venv/bin/python demo/manage.py runserver
```

Open <http://127.0.0.1:8000/admin/> and sign in with the account you created.
The demo is a local development project and uses SQLite.

See the [project specification](SPEC.md), [design](DESIGN.md), and
[task list](tasks/todo.md) for scope and progress.

## Custom dashboards

Use a Python provider and a template to show data from your own models. Optional
Apache ECharts graphs are bundled locally under Apache 2.0, with light/dark mode,
responsive SVG output and an HTML data alternative. No chart license purchase or
Node installation is required by a package consumer.

See the [dashboard guide](docs/dashboard.md) for configuration, permissions,
per-site providers, templates and examples. The demo enables an editorial provider
with entry counts, category charts and recent articles.
