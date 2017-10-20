import time
from random import sample
from biohub.utils import redis
from biohub.utils.collections import unique

from biohub.biobrick.models import Biobrick
from biohub.biobrick.serializers import BiobrickSerializer

_storage = redis.Storage('__biohub_biobrick_cache_storage__')
_views_storage = redis.Storage('__biohub_biobrick_views_storage__')


def get_client_ip(request):

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


class BrickViewsManager:
    """
    A manager class to handle view counts of bricks.
    """

    def __init__(self):
        self._cache = _views_storage

    def _get_hash(self, request):

        user = request.user
        user_id = str(user.id if user.is_authenticated() else '')

        return user_id + get_client_ip(request)

    def handle_request(self, request, brick_name):

        now = int(time.time())
        self._cache.zadd(brick_name, now, self._get_hash(request))
        self._cache.zremrangebyscore(brick_name, '-inf', now - 7200)  # Expires data out of 2 hours

        count = self._cache.zcount(brick_name, '-inf', '+inf')
        self._cache.zadd('views', count, brick_name)
        self._cache.zremrangebyrank('views', 0, -51)

    def get_by_random(self, n=4):

        part_names = [name.decode() for name in self._cache.zrange('views', 0, -1)]

        if len(part_names) < n:
            selected = part_names
        else:
            selected = sample(part_names, n)

        return brick_getter.get(*selected)


class BrickGetter:
    """
    The class can be used to obtain bricks by a list of part_names, whilst the
    data fetched will be cached.
    """

    def __init__(self):
        self._cache = _storage

    def get_related_bricks(self, part_name):
        """
        Efficiently get subparts of given brick.
        """

        key = 'rel_' + part_name
        subparts = self._cache.get(key)

        if subparts is None:
            try:
                brick = Biobrick.objects.only('part_name', 'ruler').get(part_name=part_name)
            except Biobrick.DoesNotExist:
                subparts = []

            subparts = ['BBa_' + item['short_name'] for item in (brick.ruler['sub_parts'] or [])]
            self._cache.set(key, subparts)

        return self.get(*subparts)

    def get(self, *part_names):
        """
        Efficiently get a bulk of bricks
        """

        part_names = unique(part_names)
        missing = []
        results = []

        for part_name in part_names:
            value = self._cache.get(part_name)
            if value is None:
                missing.append(part_name)
            else:
                results.append(value)

        bricks = Biobrick.objects.filter(
            part_name__in=missing
        ).only(
            'part_name',
            'part_type',
            'status',
            'rate_score',
            'stars',
            'rates',
            'watches',
            'uses',
            'weight',
            'author',
            'part_status',
            'sample_status',
            'short_desc'
        )

        serializer_data = BiobrickSerializer.list_creator()(bricks, many=True).data
        for item in serializer_data:
            part_name = item['part_name']
            self._cache.set(part_name, item)
            self._cache.pexpire(part_name, 30 * 60 * 1000)  # 1 hour

        return results + serializer_data


brick_getter = BrickGetter()
brick_views_manager = BrickViewsManager()
