from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        from biohub.biobrick.serializers import CACHE_PREFIX
        from django.core.cache import cache

        cache.delete_pattern('%s*' % CACHE_PREFIX)
