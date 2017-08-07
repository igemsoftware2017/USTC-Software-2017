from django.utils.functional import cached_property

from biohub.core.tasks.exceptions import TaskInstanceNotExists
from biohub.core.tasks.storage import storage, make_key


class TaskPayload(object):
    """
    A task payload carries information related to a specific task instance,
    including task_id, arguments, options, etc.
    """

    def __init__(self, task_name, task_id, args, kwargs, options):
        self.task_name = task_name
        self.task_id = task_id
        self.args = args
        self.kwargs = kwargs or {}
        self.options = options

    def store(self):
        """
        To store the information into redis.
        """
        storage.set(make_key(self.task_id), self.packed_data)

    @cached_property
    def packed_data(self):
        """
        To pack the information into a tuple.
        """
        return (self.task_name, self.task_id, self.args,
                self.kwargs, self.options)

    @classmethod
    def from_packed_data(cls, packed_data):
        """
        A factory function to create a payload from a tuple.
        """
        return cls(*packed_data)

    @classmethod
    def from_task_id(cls, task_id):
        """
        A factory function to fetch task payload through a given task_id.
        """
        packed_data = storage.get(make_key(task_id))

        if packed_data is None:
            raise TaskInstanceNotExists(task_id)

        return cls.from_packed_data(packed_data)
