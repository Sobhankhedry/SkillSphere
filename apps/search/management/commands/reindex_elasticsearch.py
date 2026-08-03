from django.core.management.base import BaseCommand

from apps.search.indexing import bulk_index_all


class Command(BaseCommand):
    help = "Drop and recreate Elasticsearch indices, then index all data"

    def handle(self, *args, **options):
        self.stdout.write("Starting Elasticsearch reindex...")
        bulk_index_all()
        self.stdout.write(self.style.SUCCESS("Reindex complete"))
