from biohub.core.tasks.exceptions import TaskInstanceNotExists
from biohub.core.tasks.storage import storage


class TaskPayload(object):
    """
    A task payload carries information related to a specific task instance,
    including task_id, arguments, options, etc.
    """

    __slots__ = ['task_name', 'task_id', 'args', 'kwargs', 'options',
                 'packed_data']

    def __init__(self, task_name, task_id, args, kwargs, options):
        self.task_name = task_name
        self.task_id = task_id
        self.args = args
        self.kwargs = kwargs or {}
        self.options = options
        self.packed_data = (task_name, task_id, args, kwargs, options)

    def store(self):
        """
        To store the information into redis.
        """
        storage.set(self.task_id, self.packed_data)

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
        packed_data = storage.get(task_id)

        if packed_data is None:
            raise TaskInstanceNotExists(task_id)

        return cls.from_packed_data(packed_data)
