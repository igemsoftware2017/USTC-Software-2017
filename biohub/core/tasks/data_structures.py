"""
This module contains multiple classes to wrap data structures of redis.
"""

import json
import functools

from biohub.core.tasks.storage import make_key

serialize = json.dumps
deserialize = json.loads


class RedisProxy(object):
    """
    A proxy class applying given name automatically to redis client functions.
    """

    def __init__(self, name, redis):
        self._name = name
        self._redis = redis

    def __getattr__(self, name):

        target = getattr(self._redis, name)

        if callable(target):

            @functools.wraps(target)
            def func(*args, **kwargs):

                return target(self._name, *args, **kwargs)

            self.__dict__[name] = func
        else:
            self.__dict__[name] = target

        return self.__dict__[name]


class DataStructureBase(object):

    def __init__(self, name, redis):
        self._name = make_key(name)
        self._redis = RedisProxy(self._name, redis)


class Set(DataStructureBase):
    """
    Wrapper for redis's SET.
    """

    def add(self, value):
        self._redis.sadd(value)

    def remove(self, value):
        self._redis.srem(value)

    def __len__(self):
        return self._redis.scard()

    def __contains__(self, value):
        return bool(self._redis.sismember(value))

    def __iter__(self):
        yield from map(deserialize, self._redis.smembers())


class Queue(DataStructureBase):
    """
    A simple queue based on redis's LIST.
    """

    def __init__(self, *args, **kwargs):
        super(Queue, self).__init__(*args, **kwargs)

    def enqueue(self, obj):
        item = serialize(obj)
        self._redis.lpush(item)

    def dequeue(self):
        poped = self._redis.rpop()

        if poped is not None:

            return deserialize(poped)

        return None

    def rdel(self, obj):
        """
        Searches and deletes the first `obj` from the head of the queue.
        """
        item = serialize(obj)
        self._redis.lrem(-1, item)

    def __iter__(self):
        yield from map(deserialize, self._redis.lrange(0, -1))

    def __len__(self):
        return self._redis.llen()

    def __contains__(self, key):
        return self._redis.lindex(key) is not None
