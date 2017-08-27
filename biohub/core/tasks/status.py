import enum


class TaskStatus(enum.Enum):

    GONE = 'GONE'
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    TIMEOUT = 'TIMEOUT'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'

    @property
    def is_ready(self):
        return self in READY_STATUSES


READY_STATUSES = (TaskStatus.SUCCESS, TaskStatus.TIMEOUT, TaskStatus.ERROR)
