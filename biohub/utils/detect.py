import os

from django.utils.functional import cached_property


class Features:

    @cached_property
    def redis(self):
        from django.core.cache import cache
        return cache.client.__class__.__module__.startswith('django_redis')

    @property
    def testing(self):
        return 'BIOHUB_TESTING' in os.environ


features = Features()
