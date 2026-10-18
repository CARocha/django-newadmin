# django-newadmin

A modern, extensible light-and-dark theme for Django's built-in admin.

**Status:** 0.1.0a1 alpha candidate. Django 6.0 and 6.1 on Python 3.13 and 3.14
are tested locally; GitHub Actions repeats this matrix after the code is pushed.
TestPyPI publication is manual; PyPI publication runs only when a GitHub Release
uses the matching version tag. License: BSD-3-Clause.

**Documentation:** [CARocha.github.io/django-newadmin](https://carocha.github.io/django-newadmin/)
will be published by GitHub Actions after Pages is enabled for this repository.

## Development setup

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -e '.[dev,docs]'
npm ci
.venv/bin/python -m pytest tests --ignore=tests/browser -q
.venv/bin/python -m playwright install chromium
.venv/bin/python -m pytest tests/browser -q
npm run build:css
npm run build:charts
npm run build:icons
npm run test:js
```

The npm commands are for developing NewAdmin's assets. Installing the Python
package includes the compiled files and does not require Node.js.

## Activate NewAdmin

Add `newadmin` before Django's admin app. No model changes, middleware, or
migrations are required in a consuming project:

```python
INSTALLED_APPS = [
    "newadmin",
    "django.contrib.admin",
    # Other Django apps.
]
```

The theme works with its defaults. Optional site branding and appearance can be
set in `settings.py`:

```python
NEWADMIN = {
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

## Menus and extensions

Configure model/app icons, named links with permission checks, per-AdminSite
settings and custom CSS. Public template blocks let a consuming project extend
the branding, sidebar and footer while retaining Django's native controls.
See the [configuration and extension guide](docs/configuration.md).

## Documentation (Sphinx)

The Spanish user guides cover [installation](docs/installation.md),
[configuration](docs/configuration.md), [dashboards](docs/dashboard.md),
[accessibility](docs/accessibility.md) and [release steps](docs/releasing.md).
Build the searchable HTML documentation locally:

```sh
.venv/bin/python -m sphinx -n -W --keep-going -b html docs docs/_build/html
.venv/bin/python -m http.server 8002 --directory docs/_build/html
```

Open <http://127.0.0.1:8002/>. Read the [changelog](CHANGELOG.md) and alpha
limitations before using this release. `.readthedocs.yaml` is ready for connecting
a Read the Docs project; hosted documentation has not been published yet.
