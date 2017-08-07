import enum

from biohub.utils.detect import features
from biohub.core.tasks.storage import make_key, storage


class TaskStatus(enum.Enum):

    GONE = 'GONE'
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    TIMEOUT = 'TIMEOUT'
    DONE = 'DONE'


def make_task_status_key(task_id):
    return make_key(task_id + 'status')


def set_status(task_id, status):

    status = TaskStatus(status)
    key = make_task_status_key(task_id)

    if status == TaskStatus.GONE:
        storage.delete(key)
    else:

        if status in (TaskStatus.TIMEOUT, TaskStatus.DONE):
            timeout = 1.5 if features.testing else 2 * 60 * 60
        else:
            timeout = None
        storage.set(key, status, timeout=timeout)


def get_status(task_id):

    key = make_task_status_key(task_id)
    status = storage.get(key)

    if status is None:
        return TaskStatus.GONE
    else:
        return TaskStatus(status)
