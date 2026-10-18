# Troubleshooting

## Django admin still has its default appearance

Check that the package is installed in the same environment that runs Django and
that `newadmin` comes before `django.contrib.admin`. Review overrides in
`TEMPLATES['DIRS']` and applications before `newadmin`; they can shadow the theme
templates.

```sh
python -m pip show django-newadmin
python manage.py check
python manage.py findstatic newadmin/css/newadmin.css --verbosity 2
```

## Missing static files, styles, or icons

Run `collectstatic`, check `STATIC_URL` and static-file serving, and clear the
browser cache. Do not mix templates from one release with CSS from another.
`ManifestStaticFilesStorage` needs every package file in its manifest.

## Configuration errors

Theme checks distinguish invalid settings (`newadmin.E001`/`E002`), resource
paths (`E003`), menu (`E004`), and application ordering (`E005`). The message
describes the fix. `LOGO` and `CUSTOM_CSS` use staticfiles paths, without external
URLs or `..`.

If a named link cannot be resolved, check its name, namespace, and model
registration on that `AdminSite`. The theme does not fall back to another site.
Hidden models or links may be due to permissions; do not disable those checks.

## Dashboard is missing or has no data

Check the import path in `DASHBOARD`, its subclass, `template_name`, and the
user's permissions. Without permission, the generic dashboard is shown. Filter
data in the provider, not the frontend. Check the console if ECharts fails; data
should remain available in the tabular alternative.

## Customizations change contrast or controls

Check all three modes and keyboard navigation after adding CSS or widgets. Keep
`block.super` in resource blocks. Review separately any admin screens you replace
completely.

When reporting an issue, include Python/Django/NewAdmin versions, browser,
affected screen, reproduction steps, and a minimal example without credentials or
personal data.
