from django.core.management.base import BaseCommand

from apps.forum.models import LearningResource
from apps.forum.preview import refresh_resource_preview


class Command(BaseCommand):
    help = \"Refresh webpage preview metadata for learning resources.\"

    def add_arguments(self, parser):
        parser.add_argument(\"--force\", action=\"store_true\", help=\"Refresh resources even when preview data already exists.\")

    def handle(self, *args, **options):
        force = options[\"force\"]
        queryset = LearningResource.objects.all()
        if not force:
            queryset = queryset.filter(preview_image_url=\"\")

        updated = 0
        for resource in queryset:
            before = (resource.preview_image_url, resource.preview_site_name)
            refresh_resource_preview(resource, force=force)
            after = (resource.preview_image_url, resource.preview_site_name)
            if after != before:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f\"Refreshed {updated} learning resource previews.\"))
