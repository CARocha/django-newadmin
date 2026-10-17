from django.contrib import admin
from django.utils import timezone

from .models import Article, ArticleLink, ArticleSection, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class ArticleLinkInline(admin.TabularInline):
    model = ArticleLink
    extra = 0
    raw_id_fields = ("category",)


class ArticleSectionInline(admin.StackedInline):
    model = ArticleSection
    extra = 0


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "updated_at")
    list_filter = ("status", "category")
    list_editable = ("status",)
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("category",)
    filter_horizontal = ("topics",)
    date_hierarchy = "updated_at"
    list_per_page = 20
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "topics")}),
        ("Story", {"fields": ("excerpt", "body"), "classes": ("wide",)}),
        ("Publication", {"fields": ("status", "published_at"), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("created_at", "updated_at")
    inlines = (ArticleLinkInline, ArticleSectionInline)

    def save_model(self, request, obj, form, change):
        if obj.status == Article.Status.PUBLISHED and obj.published_at is None:
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)
