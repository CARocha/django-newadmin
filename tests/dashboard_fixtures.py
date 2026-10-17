from adminwp.dashboard import Dashboard, EChartsDashboard


class ExampleDashboard(Dashboard):
    template_name = "dashboard_probe.html"

    def get_context_data(self, request):
        return {"message": f"Panel for {request.user.username}", "site_header": "Injected header"}

    class Media:
        js = ["dashboard-probe.js"]


class PrivateDashboard(ExampleDashboard):
    permissions = ("catalog.view_article",)

    def get_context_data(self, request):
        raise AssertionError("A forbidden provider must not be evaluated")


class BrokenDashboard(Dashboard):
    def get_context_data(self, request):
        return []


class ChartDashboard(EChartsDashboard):
    template_name = "dashboard_charts_probe.html"

    def get_context_data(self, request):
        label = '</script><img src=x onerror="window.chartInjection=true">'
        return {
            "chart": {
                "id": "category-counts",
                "title": "Entries per category",
                "option": {
                    "legend": {},
                    "dataZoom": [{"type": "inside", "start": 0, "end": 100}],
                    "tooltip": {},
                    "xAxis": {"type": "category", "data": ["News", label]},
                    "yAxis": {"type": "value"},
                    "series": [
                        {"name": "Articles", "type": "bar", "data": [3, 5]},
                        {"name": "Drafts", "type": "bar", "data": [1, 2]},
                    ],
                },
                "columns": ["Category", "Articles", "Drafts"],
                "rows": [["News", 3, 1], [label, 5, 2]],
            }
        }


