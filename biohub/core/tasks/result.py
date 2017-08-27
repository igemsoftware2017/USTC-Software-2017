from operator import or_
from functools import reduce

from biohub.core.tasks.storage import storage
from biohub.core.tasks.status import TaskStatus
from django.utils.functional import cached_property


def get_result_timeout():
    from biohub.utils.detect import features
    return 1.5 if features.testing else 2 * 60 * 60


class AsyncResultMeta(type):

    def __new__(cls, name, bases, attrs):
        fields = reduce(
            or_,
            (
                set(getattr(base, 'properties', []))
                for base in bases if isinstance(base, AsyncResultMeta)
            ),
            set(attrs.get('properties', ()))
        )

        new_class = type.__new__(cls, name, bases, attrs)

        for field in fields:
            cls._make_property(field, new_class)

        return new_class

    @classmethod
    def _make_property(cls, name, new_class):

        getter = cls._prepare_descriptor(name, new_class, 'get', lambda self: self._get_field(name))
        cls._prepare_descriptor(name, new_class, 'set', lambda self, value: self._set_field(name, value))
        cls._prepare_descriptor(name, new_class, 'del', lambda self: self._del_field(name))

        setattr(new_class, name, property(getter))  # , setter, deleter)

    @classmethod
    def _prepare_descriptor(cls, name, new_class, action, default):
        attrname = '_{}_{}'.format(action, name)

        if hasattr(new_class, attrname):
            return getattr(new_class, attrname)
        else:
            setattr(new_class, attrname, default)
            return default


class AsyncResult(object, metaclass=AsyncResultMeta):

    properties = ['status', 'result', 'payload']

    def __init__(self, task_id):
        self._task_id = task_id
        self._storage = storage

    @cached_property
    def _storage_key(self):
        return self._task_id + '_meta'

    def _get_field(self, name):
        return self._storage.hget(self._storage_key, name)

    def _set_field(self, name, value):
        return self._storage.hset(self._storage_key, name, value)

    def _del_field(self, name):
        return self._storage.hdel(self._storage_key, name)

    def _expire(self, timeout):
        if timeout is None:
            return self._storage.persist(self._storage_key)
        else:
            timeout = int(timeout * 1000)
            return self._storage.pexpire(self._storage_key, timeout)

    def exists(self):
        return self._storage.exists(self._storage_key)

    @property
    def task_id(self):
        return self._task_id

    def _get_status(self):
        from biohub.utils.detect import features

        if hasattr(self, '_status') and not features.testing:
            return self._status

        status = self._get_field('status')

        if status is None:
            return TaskStatus.GONE
        else:
            status = TaskStatus(status)
            if status.is_ready:
                self._status = status

            return status

    def _check_ready(self):
        if hasattr(self, '_status'):
            raise ValueError('State was ready.')

    def _set_status(self, status):
        self._check_ready()

        status = TaskStatus(status)

        if status == TaskStatus.GONE:
            self._del_status()
        else:
            if status.is_ready:
                self._status = status
                self._expire(get_result_timeout())

            self._set_field('status', status)

    def _after_ready(self, state, result):
        pass

    def pend(self):
        self._set_status(TaskStatus.PENDING)

    def run(self):
        self._set_status(TaskStatus.RUNNING)

    def resolve(self, result):
        self._set_status(TaskStatus.SUCCESS)
        self._set_result(result)
        self._after_ready(TaskStatus.SUCCESS, result)

    def timeout(self):
        self._set_status(TaskStatus.TIMEOUT)
        self._after_ready(TaskStatus.TIMEOUT, None)

    def error(self, exception):
        self._set_status(TaskStatus.ERROR)
        self._set_result(exception)
        self._after_ready(TaskStatus.ERROR, None)

    def wait(self, rounds, duration):
        import time

        while rounds >= 0:
            time.sleep(duration)

            if self.status.is_ready:
                return True

            rounds -= 1

        return False
