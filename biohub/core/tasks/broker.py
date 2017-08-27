from uuid import uuid4

from channels import Channel

from biohub.core.conf import settings as biohub_settings
from biohub.core.tasks.registry import tasks
from biohub.core.tasks.payload import TaskPayload
from biohub.core.tasks.data_structures import Queue, Set
from biohub.core.tasks.result import AsyncResult


def get_task_id(task_name):
    """
    Generates a random and unique id for a specific task instance.
    """
    return str(uuid4())


class Broker(object):
    """
    A manager class to handle tasks queuing, starting.
    """

    def __init__(self, name, max_tasks=None, timeout=None):
        """
        name: namespace for keys of redis objects.
        max_tasks: the maximum number of tasks running at a time, default to
            `biohub_settings.BIOHUB_MAX_TASKS`.
        timeout: the maximum timeout of a task, default to
            `biohub_settings.BIOHUB_TASK_MAX_TIMEOUT`.
        """
        from django_redis import get_redis_connection

        redis_client = get_redis_connection('default')

        self._max_tasks = (max_tasks if max_tasks is not None
                           else biohub_settings.BIOHUB_MAX_TASKS)
        self._timeout = (timeout if timeout is not None
                         else biohub_settings.BIOHUB_TASK_MAX_TIMEOUT)
        self._pending_queue = Queue('%s_pending_queue' % name, redis_client)
        self._running_set = Set('%s_running_set' % name, redis_client)

    def _enqueue_task(self, task_id):
        """
        Puts a task into the task queue, after which checks if there're tasks
        available to run.
        """
        self._pending_queue.enqueue(task_id)
        AsyncResult(task_id).pend()
        self._dequeue_task()

    def _dequeue_task(self):
        """
        Checks if there're tasks available to run, and starts them if yes.
        """
        while len(self._pending_queue) < self._max_tasks:
            popped_task_id = self._pending_queue.dequeue()
            if popped_task_id is None:
                return

            self._dispatch_task(popped_task_id)

    def _dispatch_task(self, task_id):
        """
        To actually apply a task, by pushing the task id into the running
        set and sending the id to a channel worker.
        """
        self._running_set.add(task_id)
        AsyncResult(task_id).run()

        Channel('task').send({'task_id': task_id})

    def _invalidate_task(self, task_id):
        """
        To mark a task instance finished, by removing its id out of running and
        pending queue.

        Note that this function will NOT set the status of the task, which
        should be set by the caller since there're multiple reasons for a
        task's finishing (timeout, success or error, etc.).
        """
        self._running_set.remove(task_id)
        self._pending_queue.rdel(task_id)

    def _task_done(self, task_class, task_id):
        """
        To invalidate a finished task, and check if there're new tasks
        available to run.

        This function is called by `run_task`.
        """
        self._invalidate_task(task_id)

        self._dequeue_task()

    def _validate_options(self, options):
        """
        To extract and validate running options from the argument `options`.
        """
        validated = {}
        validated['timeout'] = min(
            options.get('timeout', self._timeout),
            self._timeout
        )

        return validated

    def apply_async(self, task, args=(), kwargs=None, **options):
        """
        Given arguments and running options, creates and pends a task instance.

        task: a string or a subclass of Task. If it's a string, it should be a
            registered task name, otherwise a TypeError raised.
        args: positional arguments to be passed to the task, whose items
            must be pickleable.
        kwargs: keyword arguments to be passed to the task, whose items must be
            pickleable.
        options: running options:
            - timeout: timeout setting of the task, which should not exceed
                the default timeout of the broker.
        """
        from biohub.core.tasks import Task

        # Type checks.
        if isinstance(task, str):
            task_class = tasks[task]
        elif issubclass(task, Task):
            task_class = task
        else:
            raise TypeError(
                "`task` should either be a str or a subclass of Task,"
                " got '%s'."
                % type(task))

        task_name = task_class.task_name
        options = self._validate_options(options)
        task_id = get_task_id(task_name)
        TaskPayload(task_name, task_id, args, kwargs, options).store()

        self._enqueue_task(task_id)

        return task_class.async_result(task_id)

    def run_task(self, task_id):
        """
        To actually run a task in current process.

        This function is called by channel handlers and not suggested to be
        called manually.
        """
        payload = TaskPayload.from_task_id(task_id)

        try:
            task_class = tasks[payload.task_name]
            task_class.execute(payload)
        finally:
            self._task_done(task_class, task_id)


broker = Broker('default')

apply_async = broker.apply_async
