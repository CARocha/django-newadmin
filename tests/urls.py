"""URL configuration for the minimal integration-test project."""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import HttpResponse
from django.urls import path

import demo.catalog.admin  # noqa: F401
from demo.catalog.models import Article, Category

operations_site = AdminSite(name="operations")
operations_site.register(Article)
operations_site.register(Category)


def report_view(request):
    return HttpResponse("Reports")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("operations/", operations_site.urls),
    path("reports/", report_view, name="report"),
    path("informes/niñez/", report_view, name="unicode-report"),
]
