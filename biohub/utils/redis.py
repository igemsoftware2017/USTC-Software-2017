import inspect
from functools import partial, wraps

_redis_func_template = """
def {funcname}{arguments}:
    {patch_arguments}
    result = self._redis_client.{funcname}({passing_arguments})
    if is_value:
        result = self.decode(result)
    elif is_iter:
        result = map(self.decode, result)
    return result
"""


class Storage(object):

    return_value_funcs = 'lpop rpop lindex hget rpoplpush spop'.split()
    return_iter_funcs = 'smembers hmget hvals lrange mget sdiff sinter'.split()

    def __init__(self, namespace):

        from django.core.cache import cache
        from django_redis import get_redis_connection

        self._namespace = namespace
        self._redis_client = get_redis_connection('default')

        old = cache._client
        cache._client = None
        client = self._cache_client = cache.client
        cache._client = old

        old_make_key = client.make_key

        @wraps(old_make_key)
        def make_key(key, version=None, prefix=None):
            key = namespace + key

            return old_make_key(key, version, prefix)

        client.make_key = make_key

    def decode(self, value):
        if value is not None:
            value = self._cache_client.decode(value)

        return value

    def strip(self, *keys):
        prefix = self.make_key('')
        prefix_length = len(prefix)

        for key in keys:
            if key.startswith(prefix):
                yield key[prefix_length:]
            else:
                yield key

    def _wrap_cache_func(self, func):

        return func

    def _wrap_redis_func(self, func):

        signature = inspect.signature(func)
        parameters = signature.parameters

        funcname = func.__name__
        arguments = str(signature)

        patching_statements = {
            'name': 'name = self.make_key(name)',
            'names': 'names = map(self.make_key, names)',
            'value': 'value = self.encode(value)',
            'values': 'values = map(self.encode, values)',
            'refvalue': 'refvalue = self.encode(refvalue)',
            'keys': 'keys = map(self.make_key, keys)',
            'key': 'key = self.make_key(key)',
            'pattern': 'pattern = self.make_key(pattern)'
        }
        patch_arguments = ';'.join(
            statement for arg, statement in patching_statements.items()
            if arg in parameters)

        passing_arguments = ','.join(
            item.split('=')[0]
            for item in arguments.strip('()').split(',')
        )

        namespace = dict(
            self=self, map=map, partial=partial,
            is_value=funcname in self.return_value_funcs,
            is_iter=funcname in self.return_iter_funcs
        )

        exec(
            _redis_func_template.format(
                funcname=funcname,
                arguments=arguments,
                patch_arguments=patch_arguments,
                passing_arguments=passing_arguments,

            ),
            namespace
        )

        result = namespace[funcname]
        result.__module__ = self.__module__

        return result

    def __getattr__(self, name):

        if hasattr(self._cache_client, name):
            value = getattr(self._cache_client, name)

            if callable(value):
                value = self._wrap_cache_func(value)
        else:
            value = getattr(self._redis_client, name)

            if callable(value):
                value = self._wrap_redis_func(value)

        self.__dict__[name] = value
        return value
