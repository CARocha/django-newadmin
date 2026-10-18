# django-newadmin

A Django administration theme built with Bootstrap, light and dark appearances,
work-focused navigation, and extensible dashboards powered by Apache ECharts.

Version **0.1.0a1** is an alpha release. Try it in a test environment first; its
API may change during the alpha series. The theme keeps Django admin and its
permissions. It needs no models, migrations, or custom `AdminSite`.

```{toctree}
:maxdepth: 2
:caption: Guides

installation
configuration
dashboard
extensions
accessibility
troubleshooting
releasing
changelog
```

## Compatibility

Python 3.13 and 3.14 with Django 6.0 and 6.1. All four combinations have local
tests, and CI runs the same matrix on GitHub. Later Django versions need a new
compatibility check.

Bootstrap, icons, and ECharts are distributed locally. Package users do not need
Node, Sass, or external chart services. The theme uses the BSD 3-Clause License;
each library retains its own license notices.
