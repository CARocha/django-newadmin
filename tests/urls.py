"""URL configuration for the minimal integration-test project."""

from django.contrib import admin
from django.urls import path

import demo.catalog.admin  # noqa: F401

urlpatterns = [path("admin/", admin.site.urls)]
