from biohub.core.tasks.registry import tasks
from biohub.core.tasks.exceptions import TaskInterruption
from biohub.core.tasks.executors import get_executor
from biohub.core.tasks.payload import TaskPayload
from biohub.core.tasks.result import AsyncResult


class TaskBase(type):

    def __new__(cls, name, bases, attrs):

        new_class = super(TaskBase, cls).__new__(cls, name, bases, attrs)

        # If it's class `Task`, ignore it.
        # Note that at this stage name `Task` is not available, so cannot use
        # `is` operator to do the check.
        if not [base for base in bases if isinstance(base, TaskBase)]:
            return new_class

        task_name = getattr(new_class, 'task_name',
                            '%s.%s' % (new_class.__module__, name))
        tasks.register(task_name, new_class)
        new_class.task_name = task_name

        return new_class


class Task(object, metaclass=TaskBase):
    """
    Base class of a task.
    """

    async_result_class = AsyncResult

    def __init__(self, arg):
        """
        `arg` should be a string or a `TaskPayload` instance. If it's a string,
        it should be a valid task_id.

        Note that the task instance is runnable only if a payload applied,
        otherwise it can just be used for state querying.
        """

        if isinstance(arg, str):
            self.task_id = arg
        elif isinstance(arg, TaskPayload):
            self.task_id = arg.task_id
            self.payload = arg
            self._interrupted = False
        else:
            raise TypeError(
                "'arg' should be either a str or a TaskPayload, got '%r'."
                % type(arg))

    @classmethod
    def async_result(cls, task_id):
        return cls.async_result_class(task_id)

    def run(self, *args, **kwargs):
        """
        The main function of a task.
        """
        raise NotImplementedError

    def interrupt(self):
        """
        Marks this task interrupted.

        This function is called by task executor and there's no necessity to
        call manually.
        """
        self._interrupted = True

    def check_interrupt(self):
        """
        Checks if this task was marked interrupted. If yes, raise an Exception
        to terminate the thread.

        A good task should call this function frequently to avoid infinite
        loop.
        """
        if not self._interrupted:
            return

        self.before_interrupt()

        raise TaskInterruption

    def before_interrupt(self):
        """
        This function will be called before the thread is terminated, which
        may be overrided to do some cleaning work.
        """
        pass

    @classmethod
    def execute(cls, payload):
        """
        Given a payload, and creates an executor to run the task.
        """
        instance = cls(payload)
        get_executor(instance).execute()

    @classmethod
    def apply_async(cls, *args, **kwargs):
        """
        This function is a proxy to `broker.apply_async`.
        """
        from biohub.core.tasks import apply_async

        return apply_async(cls, args, kwargs)
