from itertools import chain

from django_redis import get_redis_connection
from django.core.cache import cache

from biohub.utils.detect import features


CACHE_PREFIX = ('__test_biohub_tasks__'
                if features.testing else '__biohub_tasks__')


def make_key(key):
    return '{}{}'.format(CACHE_PREFIX, key)


storage = cache
redis_client = get_redis_connection('default')


def clear_keys():
    for key in chain(
            redis_client.keys(CACHE_PREFIX + '*'),
            redis_client.keys(storage.make_key(CACHE_PREFIX) + '*')):
        redis_client.delete(key)
