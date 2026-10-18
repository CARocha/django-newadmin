# Alpha development and release

## Build the documentation

```sh
python -m pip install -e '.[dev,docs]'
python -m sphinx -n -W --keep-going -b html -A newadmin_docs_language=es docs docs/_build/html
python -m sphinx -n -W --keep-going -b html -c docs -D language=en -A newadmin_docs_language=en docs/en docs/_build/html/en
python -m http.server 8002 --directory docs/_build/html
```

Sphinx uses MyST for Markdown and Furo for the site. The root is Spanish and the
English version lives under `/en/`. No Django server is needed to view the built
HTML. `.readthedocs.yaml` allows import on Read the Docs; connecting and publishing
that project is a maintainer action that has not yet been completed.

## Publish documentation on GitHub Pages

The `.github/workflows/docs.yml` workflow builds both languages with Sphinx and
deploys them after a push to `main` that changes `docs/` or `pyproject.toml`. To
enable the destination once, open the repository's
[Settings → Pages](https://github.com/CARocha/django-newadmin/settings/pages) and
select **GitHub Actions** under *Build and deployment → Source*. After saving, the
site is published at <https://carocha.github.io/django-newadmin/>. You can also
run it from Actions → **Documentation** → Run workflow.

## Verify a release candidate

```sh
npm ci
npm run build:css
npm run build:icons
npm run build:charts
npm run test:js
python -m playwright install chromium
python -m pytest -q
python -m ruff check .
python demo/manage.py check
python demo/manage.py makemigrations --check --dry-run
python -m sphinx -n -W --keep-going -b html docs docs/_build/html
python -m build
python -m twine check --strict dist/django_newadmin-0.1.0a1*
```

CI repeats the four Python/Django combinations, rebuilds assets to check they are
current, and creates the Sphinx site and package distributions as artifacts. A
second environment installs the wheel outside the checkout and runs
`scripts/smoke_wheel.py`: installed import, login, index, form, templates, and
staticfiles with manifest storage. Nothing is published automatically.

To repeat a clean local wheel install, create a separate environment, install the
wheel (without `-e`), and run the script with that interpreter:

```sh
python -m venv /tmp/newadmin-wheel-test
/tmp/newadmin-wheel-test/bin/python -m pip install dist/django_newadmin-0.1.0a1-py3-none-any.whl
/tmp/newadmin-wheel-test/bin/python scripts/smoke_wheel.py
```

The script rejects imports from the checkout to prevent a false positive.

## Connect TestPyPI and PyPI to GitHub Actions

The workflows use Trusted Publishing and do not store PyPI tokens in GitHub.
Register the repository and workflow each service will accept in both TestPyPI
and PyPI. Enable two-factor authentication on both accounts.

On [TestPyPI](https://test.pypi.org), sign in, open Account settings → Publishing,
and register a **pending publisher** with these values:

| Field | Value |
| --- | --- |
| PyPI project name | `django-newadmin` |
| Owner | `CARocha` |
| Repository name | `django-newadmin` |
| Workflow name | `publish-testpypi.yml` |
| Environment name | `testpypi` |

Then open Actions → **Publish to TestPyPI** in GitHub and run the workflow from
`main`. It builds and verifies distributions before uploading them. The first
publication creates the project on TestPyPI; a pending publisher does not reserve
the name until used.

Test the TestPyPI installation in a temporary environment, with Django installed
from PyPI:

```sh
python -m venv /tmp/test-newadmin
/tmp/test-newadmin/bin/python -m pip install 'Django>=6.0,<6.2'
/tmp/test-newadmin/bin/python -m pip install \
  --index-url https://test.pypi.org/simple/ --no-deps django-newadmin
```

On [PyPI](https://pypi.org), sign in and register another pending publisher from
Account settings → Publishing:

| Field | Value |
| --- | --- |
| PyPI project name | `django-newadmin` |
| Owner | `CARocha` |
| Repository name | `django-newadmin` |
| Workflow name | `publish-pypi.yml` |
| Environment name | `pypi` |

After verifying TestPyPI, create a GitHub Release for the version tag, for example
`v0.1.0a1`. Publishing the release triggers the PyPI workflow. Confirm that the
tag points to the approved version commit and CI passed. PyPI does not allow
re-uploading an existing version.

The first alpha must be registered on both indexes. TestPyPI and PyPI uploads are
separate; publishing to one does not publish to the other.

## Build distributions locally

You can build manually with Twine to debug a release. The normal flow uses Trusted
Publishing. The candidate is `0.1.0a1`. Enable two-factor authentication on both
accounts and confirm CI passed. Manual upload uses separate accounts and tokens
for each index.

```sh
python -m twine upload --repository testpypi dist/django_newadmin-0.1.0a1-py3-none-any.whl dist/django_newadmin-0.1.0a1.tar.gz
```

Test this artifact with Django installed from PyPI, so dependencies are not
resolved from TestPyPI:

```sh
python -m pip install 'Django>=6.0,<6.2'
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps 'django-newadmin==0.1.0a1'
```

After verification, the same files can be uploaded to PyPI:

```sh
python -m twine upload dist/django_newadmin-0.1.0a1-py3-none-any.whl dist/django_newadmin-0.1.0a1.tar.gz
```

Record the release in the changelog and create tag `v0.1.0a1` on the verified
commit. Do not reuse an uploaded version; publish a new alpha for a fix. Keep the
SHA-256 hashes of the artifacts.

If a problem occurs, document its scope and release a corrected alpha. A user
can pin an earlier version or disable `newadmin`; the theme has no migrations of
its own. The first alpha has no previous version.

References: [Sphinx](https://www.sphinx-doc.org/en/master/usage/quickstart.html),
[packaging and TestPyPI](https://packaging.python.org/en/latest/tutorials/packaging-projects/),
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/),
[creating a project with a Trusted Publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/),
[GitHub Pages with workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
