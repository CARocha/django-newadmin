from django.core.management.base import BaseCommand

from demo.catalog.models import Article, Category


class Command(BaseCommand):
    help = "Create a small, repeatable editorial dataset for the AdminWP demo."

    def handle(self, *args, **options):
        news, _ = Category.objects.update_or_create(slug="news", defaults={"name": "News"})
        design, _ = Category.objects.update_or_create(slug="design", defaults={"name": "Design"})
        examples = [
            ("A calmer workspace", "calmer-workspace", news, Article.Status.PUBLISHED),
            ("Designing for focus", "designing-for-focus", design, Article.Status.PUBLISHED),
            ("Notes from the studio", "notes-from-studio", design, Article.Status.DRAFT),
            ("A new chapter", "a-new-chapter", news, Article.Status.SCHEDULED),
        ]
        for title, slug, category, status in examples:
            Article.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "category": category,
                    "status": status,
                    "excerpt": "A sample entry for exploring the Django admin.",
                    "body": "This content is managed by Django's native admin.",
                },
            )
        self.stdout.write(self.style.SUCCESS("Demo catalog is ready."))
