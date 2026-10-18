# Changelog

## 0.1.0a1 — 2026-10-17 (initial alpha)

### Added

- Bootstrap theme for Django's built-in admin: login, navigation, changelists,
  forms, inlines, relationship widgets, history, deletion, and account pages.
- Light, dark, and automatic modes with a subtle glass finish.
- Extensible Python dashboards and locally bundled Apache ECharts, with tabular data.
- Branding, icons, permission-checked links, custom CSS, and per-AdminSite settings.
- Sphinx documentation for installation, configuration, and extensions.
- Django 6.0/6.1 and Python 3.13/3.14 test matrix; assets included in the wheel.

### Fixed

- Dashboard header adapts to narrow screens and enlarged text.
- Icon navigation links keep an explicit accessible name.

### Limitations

- First alpha: API and appearance may change; test before production use.
- Consumer customizations and third-party widgets need their own validation.
- Automated accessibility checks do not amount to WCAG certification.
