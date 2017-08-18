"""
This module contains multiple classes to wrap data structures of redis.
"""

import functools

from biohub.core.tasks.storage import storage


class RedisProxy(object):
    """
    A proxy class applying given name automatically to redis client functions.
    """

    def __init__(self, name):
        self._name = name
        self._storage = storage

    def __getattr__(self, name):

        target = getattr(self._storage, name)

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
        self._name = name
        self._storage = RedisProxy(self._name)


class Set(DataStructureBase):
    """
    Wrapper for redis's SET.
    """

    def add(self, value):
        self._storage.sadd(value)

    def remove(self, value):
        self._storage.srem(value)

    def __len__(self):
        return self._storage.scard()

    def __contains__(self, value):
        return bool(self._storage.sismember(value))

    def __iter__(self):
        return self._storage.smembers()


class Queue(DataStructureBase):
    """
    A simple queue based on redis's LIST.
    """

    def __init__(self, *args, **kwargs):
        super(Queue, self).__init__(*args, **kwargs)

    def enqueue(self, obj):
        self._storage.lpush(obj)

    def dequeue(self):
        return self._storage.rpop()

    def rdel(self, obj):
        """
        Searches and deletes the first `obj` from the head of the queue.
        """
        self._storage.lrem(-1, obj)

    def __iter__(self):
        return self._storage.lrange(0, -1)

    def __len__(self):
        return self._storage.llen()

    def __contains__(self, key):
        return self._storage.lindex(key) is not None
