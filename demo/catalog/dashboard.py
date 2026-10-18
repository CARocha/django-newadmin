"""Example: an editorial dashboard backed by this demo's own models."""

from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from newadmin.dashboard import EChartsDashboard

from .models import Article


class EditorialDashboard(EChartsDashboard):
    template_name = "newadmin/dashboard/editorial.html"
    permissions = ("catalog.view_article",)

    def get_queryset(self, request):
        # All articles are available to staff with this demo's view permission.
        # A consuming project must apply its user/tenant scope here.
        return Article.objects.all()

    def get_context_data(self, request):
        articles = self.get_queryset(request)
        stats = articles.aggregate(
            total=Count("pk"),
            published=Count("pk", filter=Q(status=Article.Status.PUBLISHED)),
            draft=Count("pk", filter=Q(status=Article.Status.DRAFT)),
        )
        categories = list(
            articles.values("category__name")
            .annotate(total=Count("pk"))
            .order_by("-total", "category__name")[:8]
        )
        category_rows = [
            [row["category__name"] or _("Uncategorized"), row["total"]] for row in categories
        ]
        start = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        start -= timedelta(days=6)
        daily = {
            row["day"]: row
            for row in articles.filter(
                created_at__gte=start, created_at__lt=start + timedelta(days=7)
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(
                published=Count("pk", filter=Q(status=Article.Status.PUBLISHED)),
                draft=Count("pk", filter=Q(status=Article.Status.DRAFT)),
            )
        }
        days = [(start + timedelta(days=n)).date() for n in range(7)]
        metrics = []
        for status, label, tone in (
            ("published", _("Published"), "success"),
            ("draft", _("Drafts"), "warning"),
        ):
            rows = [[day.isoformat(), daily.get(day, {}).get(status, 0)] for day in days]
            metrics.append(
                {
                    "label": label,
                    "value": stats[status],
                    "tone": tone,
                    "share": stats[status] / stats["total"] * 100 if stats["total"] else 0,
                    "chart": {
                        "id": f"editorial-{status}",
                        "title": _("Created in the last 7 days, by current status"),
                        "columns": [_("Date"), label],
                        "rows": rows,
                        "option": {
                            "grid": {"left": 0, "right": 0, "top": 8, "bottom": 0},
                            "tooltip": {"trigger": "axis"},
                            "xAxis": {
                                "type": "category",
                                "show": False,
                                "data": [row[0] for row in rows],
                            },
                            "yAxis": {"type": "value", "show": False, "minInterval": 1},
                            "series": [
                                {
                                    "name": label,
                                    "type": "bar",
                                    "barWidth": "70%",
                                    "data": [row[1] for row in rows],
                                }
                            ],
                        },
                    },
                }
            )
        site = getattr(request, "current_app", "admin")
        latest = [
            {
                "title": article.title,
                "category": article.category.name if article.category else _("Uncategorized"),
                "status": article.status,
                "status_label": article.get_status_display(),
                "updated_at": article.updated_at,
                "url": reverse("admin:catalog_article_change", args=[article.pk], current_app=site),
            }
            for article in articles.select_related("category").order_by("-updated_at")[:8]
        ]
        return {
            "total": stats["total"],
            "metrics": metrics,
            "latest": latest,
            "list_url": reverse("admin:catalog_article_changelist", current_app=site),
            "add_url": reverse("admin:catalog_article_add", current_app=site)
            if request.user.has_perm("catalog.add_article")
            else None,
            "category_chart": {
                "id": "editorial-categories",
                "title": _("Entries by category"),
                "description": _("Up to 8 categories with the most entries"),
                "columns": [_("Category"), _("Entries")],
                "rows": category_rows,
                "option": {
                    "tooltip": {"trigger": "axis"},
                    "grid": {
                        "left": 20,
                        "right": 40,
                        "top": 20,
                        "bottom": 24,
                        "containLabel": True,
                    },
                    "xAxis": {"type": "value", "minInterval": 1},
                    "yAxis": {
                        "type": "category",
                        "inverse": True,
                        "data": [row[0] for row in category_rows],
                        "axisLabel": {"width": 100, "overflow": "truncate"},
                    },
                    "series": [
                        {
                            "name": _("Entries"),
                            "type": "bar",
                            "barMaxWidth": 24,
                            "data": [row[1] for row in category_rows],
                            "label": {"show": True, "position": "right"},
                        }
                    ],
                },
            },
        }
