from django.contrib import admin
from django.urls import path

from demo.catalog.models import Article

reports_site = admin.AdminSite(name="reports")
reports_site.register(Article)

urlpatterns = [path("admin/", admin.site.urls), path("reports/", reports_site.urls)]
