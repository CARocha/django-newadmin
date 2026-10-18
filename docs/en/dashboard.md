# Dashboards with Apache ECharts

NewAdmin lets you replace the dashboard content with a Python class and a
template. Django admin still handles access, sessions, and native permissions.
You do not need to change `ModelAdmin` registrations or create another
`AdminSite`.

## Enable a dashboard

Without extra settings, the dashboard shows authorized applications and recent
activity. It does not load the chart library.

To enable the editorial example in the demo project:

```python
NEWADMIN = {
    "SITE_HEADER": "NewAdmin",
    "DASHBOARD": "demo.catalog.dashboard.EditorialDashboard",
}
```

The demo requires its `Article` and `Category` models. A consumer project should
create its own provider instead of depending on demo models.

## Write a provider

```python
# news/admin_dashboard.py: example for a project with news.Article.
from django.db.models import Count

from newadmin.dashboard import EChartsDashboard
from .models import Article


class NewsDashboard(EChartsDashboard):
    template_name = "news/admin/dashboard.html"
    permissions = ("news.view_article",)

    def get_context_data(self, request):
        # For a multi-organization project, filter by user or organization here
        # before aggregating. This example is for a single site.
        articles = Article.objects.all()
        counts = list(
            articles.values("category__name")
            .annotate(total=Count("pk"))
            .order_by("-total")[:8]
        )
        rows = [[row["category__name"] or "Uncategorized", row["total"]]
                for row in counts]
        return {
            "categories": {
                "id": "news-categories",
                "title": "Articles by category",
                "description": "The eight categories with the most articles",
                "columns": ["Category", "Articles"],
                "rows": rows,
                "option": {
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "category", "data": [row[0] for row in rows]},
                    "yAxis": {"type": "value", "minInterval": 1},
                    "series": [{"name": "Articles", "type": "bar",
                                "data": [row[1] for row in rows]}],
                },
            },
        }
```

```python
# settings.py
NEWADMIN = {"DASHBOARD": "news.admin_dashboard.NewsDashboard"}
```

```django
{% extends "newadmin/dashboard/layout.html" %}

{% block dashboard_title %}Editorial overview{% endblock %}

{% block dashboard_primary %}
  {% include "newadmin/dashboard/chart.html" with chart=dashboard_data.categories %}
{% endblock %}
```

The provider receives `request`, is instantiated per request, and returns a
mapping. Its context is available under `dashboard_data`; it does not replace
permission, branding, session, or AdminSite application context. An invalid
import, incorrect class, or invalid context type raises `ImproperlyConfigured`.

`permissions` requires every listed permission before querying data or evaluating
`Media`. If the user lacks permission, the authorized generic dashboard appears.
Override `has_permission(request)` for additional rules. A model permission does
not automatically filter by organization or object; the provider must enforce
those rules in its querysets before aggregating or counting.

The custom dashboard applies to the main index. Application indexes, changelists,
and forms keep their own screens and share the theme palette, header, and
navigation. Selecting a provider changes only the dashboard content; no provider
is needed to style the rest of the admin. Login and popups use the same palette
in a compact frame.

## Templates and components

`newadmin/dashboard/layout.html` exposes these blocks:

| Block | Purpose |
|---|---|
| `dashboard_title` | Dashboard title |
| `dashboard_actions` | Actions with real URLs and permissions |
| `dashboard_primary` | Main column, 8/12 from 1200 px |
| `dashboard_metrics` | Metrics column, 4/12 from 1200 px |
| `dashboard_tables` | Full-width table or content |
| `dashboard_secondary` | Links, activity, or other follow-up content |

Blocks can include project templates, HTML tables, and Bootstrap components. The
layout stacks on mobile and uses the same light and dark styles. For a completely
different layout, `template_name` can point to another content template. It must
not include a complete HTML document or duplicate the admin frame.

The `newadmin/dashboard/chart.html` component accepts `chart`:

- `id`: unique, valid HTML identifier. `chart_id` can change it when reusing a chart.
- `title`: visible, accessible title. `description` is optional.
- `option`: ECharts options serializable as JSON, without JavaScript functions.
- `columns`: headings for the tabular alternative.
- `rows`: rows of data presented by the chart.

Rows are required for the accessible alternative. If empty, the component shows
an empty state. It escapes cell HTML and uses `json_script` for data. The adapter
forces text tooltips, not HTML tooltips.

The `newadmin/dashboard/metric.html` component accepts `metric` with `label`,
`value`, `share` (actual percentage), `tone` (`success`, `warning`, or neutral),
and an optional `chart`. The demo calculates percentages from real counts. Its
sparklines show entries created in the last seven days, grouped by their current
status; they do not show status-change history.

## Separate sites and resources

```python
NEWADMIN = {
    "DASHBOARD": "news.admin_dashboard.NewsDashboard",
    "SITES": {"operations": {"DASHBOARD": None}},
}
```

`SITES` keys are `AdminSite` instance names. `None` keeps the generic dashboard
for that site. Providers do not share instances or data between requests.

You can subclass `Dashboard` for a panel without ECharts. `EChartsDashboard`
includes the local runtime and adapter. A `Media` class adds custom CSS or
JavaScript and keeps inherited resources through Django's native mechanism:

```python
class NewsDashboard(EChartsDashboard):
    # ...
    class Media:
        css = {"all": ["news/dashboard.css"]}
        js = ["news/dashboard.js"]
```

In Django 6.1, Media rendering uses Django's native nonce mechanism when the
context provides one. A specific CSP policy and consumer customizations need
their own review; enabling `unsafe-eval` is not required.

## Behavior and limits

- Charts use SVG and resize with their container. They respect light/dark/auto
  mode and reduced-motion preferences.
- Changing theme keeps legend selection and zoom range.
- ECharts provides ARIA descriptions; tabular data remains available without
  JavaScript. This alone does not certify keyboard access or full WCAG compliance.
- The adapter initializes charts present at page load. If a project inserts
  charts dynamically, it must manage their lifecycle with its own JavaScript and
  the ECharts API.
- Initialization errors are logged in the console, and tabular data remains
  available. There are no CDN or export-service requests.
- The theme does not create automatic queries for arbitrary models. Providers
  choose filters, aggregations, limits, and business rules.

## Distribution and development

ECharts 6.1.0 is pinned in npm. The Python package includes its compiled runtime,
LICENSE, NOTICE, and notices for d3, zrender, and tslib. There is no license fee
to enable these charts. Keep those notices when redistributing the resources.

```sh
npm ci
npm run build:charts
npm run build:css
```

These commands are for theme development. Installing the wheel does not require
Node. The full ECharts build is distributed to support consumer chart types; it
is about 1.1 MB minified and loads only when the provider declares those assets.

References: [ECharts options](https://echarts.apache.org/en/option.html),
[themes](https://echarts.apache.org/handbook/en/concepts/style/),
[license](https://github.com/apache/echarts/blob/master/LICENSE).
