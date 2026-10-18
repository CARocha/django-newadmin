# Configuration, navigation, and extension

Enable the theme by placing `newadmin` before `django.contrib.admin` in
`INSTALLED_APPS`. No special `ModelAdmin` or `AdminSite` is required.

## Options and defaults

| Option | Default | Purpose |
|---|---|---|
| `SITE_TITLE` | `None` | Browser title; inherits `AdminSite.site_title` |
| `SITE_HEADER` | `None` | Brand; inherits `AdminSite.site_header` |
| `LOGO` | `None` | Relative image path in staticfiles |
| `DEFAULT_MODE` | `"auto"` | `light`, `dark`, or `auto`; saved preference takes precedence |
| `PALETTE` | `"sapphire"` | Only supported palette in this alpha; customize tokens with CSS |
| `MENU.ORDER` | `[]` | Default native application order |
| `MENU.ICONS` | `{}` | Default icons for applications and models |
| `MENU.LINKS` | `[]` | Additional permission-checked links |
| `CUSTOM_CSS` | `[]` | Relative paths to extra stylesheets |
| `DASHBOARD` | `None` | Generic dashboard or importable provider path |
| `SITES` | `{}` | Overrides by `AdminSite` instance name |

All options are optional. Example:

```python
NEWADMIN = {
    "SITE_TITLE": "My studio",
    "SITE_HEADER": "Editorial administration",
    "LOGO": "branding/logo.svg",
    "DEFAULT_MODE": "auto",
    "MENU": {
        "ORDER": ["catalog", "auth"],
        "ICONS": {"catalog": "folder", "catalog.article": "file-text",
                  "catalog.category": "tag", "auth.user": "users"},
        "LINKS": [{"LABEL": "Reports", "URL_NAME": "reports:index",
                   "ICON": "chart", "PERMISSIONS": ["reports.view_report"]}],
    },
    "CUSTOM_CSS": ["branding/admin.css"],
}
```

`catalog`, `article`, `category`, and `reports:index` are examples. Use names
from your own applications, models, and routes. Settings are validated by
`python manage.py check` and when the theme resolves them.

## Order, icons, and links

`ORDER` uses `app_label` values without duplicates. Applications omitted from the
list keep their native order after the listed applications. This setting never
grants permissions or adds models that Django has not authorized for that user
and site.

`ICONS` accepts lowercase `app_label` and `app_label.model_name` keys. A model's
icon takes precedence over its application's icon. Defaults are `file-text` for
models and `folder` for applications. Stable identifiers include:

`grid`, `file-text`, `users`, `settings`, `folder`, `image`, `calendar`, `chart`,
`tag`, `database`, `globe`, `link`.

SVGs are local and decorative; labels still name each entry. The package includes
a subset of Bootstrap Icons 1.13.1 and its [MIT license](https://github.com/twbs/icons/blob/v1.13.1/LICENSE),
without fonts or a CDN. The application-list template retains Django's BSD
license in `newadmin/vendor/django/LICENSE`. Theme developers can rebuild the
sprite with `npm run build:icons`. Installing the wheel does not require npm or
Node.

Each additional link requires `LABEL` and `URL_NAME`; `ICON` defaults to `link`
and `PERMISSIONS` to `[]`. A link is shown only if the user has **all** listed
permissions. Permissions are checked before resolving its URL.

`URL_NAME` must be a named internal route without arguments. Arbitrary URLs, HTML,
callbacks, and JavaScript are not accepted. `admin:view_name` uses the current
AdminSite instance, for example `admin:catalog_article_changelist`. A missing
route or one not registered on that site raises `ImproperlyConfigured` with the
link's position; the theme does not silently fall back to another site. An
explicit project namespace keeps its destination.

The theme hides links, but the destination view must enforce its own permissions
(for example, with `admin_site.admin_view()` and a business-permission check).
Adding a link to the menu does not protect a public view.

The native filter still searches model names; extra icons and links do not change
its results. An extra link is marked active when its URL exactly matches the
current page.

## Multiple AdminSite instances

`SITES` keys are `AdminSite(name=...)` instance names, regardless of the URL
prefix where they are mounted:

```python
from django.contrib.admin import AdminSite
from django.urls import path
from news.models import Article

operations = AdminSite(name="operations")
operations.register(Article)
urlpatterns = [path("operations/", operations.urls)]

NEWADMIN = {
    "SITE_HEADER": "Administration",
    "SITES": {"operations": {
        "SITE_HEADER": "Operations",
        "CUSTOM_CSS": ["branding/operations.css"],
        "MENU": {"ORDER": ["news"], "LINKS": []},
    }},
}
```

Mappings are merged recursively; lists are replaced in full. `None` keeps its
meaning: for example, `SITE_HEADER=None` uses the AdminSite header and
`DASHBOARD=None` keeps the generic dashboard. An unconfigured site inherits the
global values. Each request gets independent options, and Django keeps the
current site's model registrations and permissions.

The light/dark/auto preference is shared by origin and browser, as in Django.
Desktop sidebar collapse and filtering keep native storage. On mobile, the menu
starts closed on every page and does not change the desktop preference. See
[accessibility and responsive behavior](accessibility.md).

## Custom CSS

`LOGO` and `CUSTOM_CSS` are relative staticfiles paths. External URLs, absolute
paths, `..` segments, backslashes, queries, and fragments are rejected. They work
with `collectstatic` and manifest storage.

On standard templates, `CUSTOM_CSS` loads after theme styles, native page styles,
and `ModelAdmin.Media` CSS. The `--newadmin-*` variables customize the appearance.
For colors that map to Django's native variables, define values on `:root` or
`html`, for example:

```css
html[data-theme="light"] {
  --newadmin-primary: #184c40;
  --newadmin-primary-hover: #123b31;
}
```

Also design the dark and automatic variants when changing colors that need them.
Keep sufficient contrast for text, controls, and focus indicators.

## Template blocks

Put overrides in a directory from `TEMPLATES['DIRS']` or in an application
installed before `newadmin`. Extend the same template name and use `block.super`
to keep the theme's content and resources:

```django
{% extends "admin/base_site.html" %}
{% block newadmin_branding %}{{ block.super }}{% endblock %}
{% block newadmin_footer %}<p>Editorial team help</p>{% endblock %}
```

```django
{% extends "admin/nav_sidebar.html" %}
{% block newadmin_sidebar_extra %}
  {{ block.super }}
  {# Project-specific content, with its permission checks. #}
{% endblock %}
```

`newadmin_branding` is inside the header brand, `newadmin_sidebar_extra` follows
the applications and includes `MENU.LINKS` by default, and `newadmin_footer` is
at the bottom of the document. The blocks receive the usual admin context. The
footer is empty by default.

Native blocks (`branding`, `extrastyle`, `responsive`, `extrahead`, `content`,
and others) remain available. Keep `block.super` when adding resources. Widgets,
inlines, and `ModelAdmin.Media` keep Django's native loading; the theme does not
require replacements or install a rich-text editor. Complete consumer overrides
and third-party integrations need their own visual review.

See [dashboard.md](dashboard.md) for custom data panels.
