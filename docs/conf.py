"""Sphinx configuration; build with sphinx-build -n -W --keep-going."""

from newadmin import __version__

project = "django-newadmin"
author = "CARocha and contributors"
copyright = "2026, CARocha and contributors"
release = __version__
version = release
language = "es"
extensions = ["myst_parser", "sphinx.ext.autodoc"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
exclude_patterns = ["_build", "en", "en/**", "proposals", "superpowers"]
html_theme = "furo"
html_title = f"{project} {release}"
templates_path = ["_templates"]
html_static_path = ["_static"]
html_css_files = ["newadmin-docs.css"]
nitpicky = True
