# django-adminwp

A WordPress-inspired, light-and-dark theme for Django's built-in admin.

**Status:** early development. Django 6.0 and 6.1 on Python 3.13 and 3.14 are
the first target matrix. This target has not yet been verified in CI.

## Development setup

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
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
