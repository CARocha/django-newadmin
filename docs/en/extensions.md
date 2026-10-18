# Extension reference

The [configuration guide](configuration.md) covers settings, icons,
permission-checked links, separate admin sites, and template blocks. The
[dashboard guide](dashboard.md) includes category aggregation, templates,
tabular alternatives, and data isolation.

## Python dashboard API

```{eval-rst}
.. autoclass:: newadmin.dashboard.Dashboard
   :members: has_permission, get_context_data

.. autoclass:: newadmin.dashboard.EChartsDashboard
```

`template_name` selects a content template. `permissions` lists Django
permissions required before data is fetched. It does not enforce object-level or
organization-level permissions; apply those in your querysets too. `Media` works
like it does for Django widgets and keeps inherited resources.

## Third-party resources and widgets

The theme keeps native scripts, inlines, and `django.jQuery`; it does not add a
second copy of jQuery. Declare widget resources in their usual `Media` class.

No rich-text editor is installed. TinyMCE, StreamField, or other widgets can be
added to the consumer project, but their versions and styles need independent
testing. They are not advertised as supported integrations in this alpha.

Do not rely on private Python functions, DOM internals, or names prefixed with
`_`. Public extension points are `NEWADMIN`, documented blocks, providers, and
visual tokens. These may change during the alpha, with migration notes.
