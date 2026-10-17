from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        SCHEDULED = "scheduled", "Scheduled"

    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles"
    )
    excerpt = models.CharField(max_length=240, blank=True)
    body = models.TextField(blank=True, help_text="Write the story content.")
    status = models.CharField(max_length=12, choices=Status, default=Status.DRAFT)
    published_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class ArticleLink(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="links")
    label = models.CharField(max_length=80)
    url = models.URLField()

    class Meta:
        ordering = ["pk"]
        verbose_name = "article link"
        verbose_name_plural = "article links"

    def __str__(self):
        return self.label


class ArticleSection(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="sections")
    heading = models.CharField(max_length=120)
    body = models.TextField(blank=True)

    class Meta:
        ordering = ["pk"]
        verbose_name = "article section"
        verbose_name_plural = "article sections"

    def __str__(self):
        return self.heading
