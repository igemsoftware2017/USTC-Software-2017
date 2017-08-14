"""
This module contains multiple implementation of task executors.

Note that ProcessExecutor is currently not available, since channel workers are
daemonatic processes, which are not allowed to have child processes. The
problem remains to be solved.
"""

import functools
import asyncio
import concurrent.futures

from biohub.core.tasks.status import set_status


class Executor(object):

    def __init__(self, task_instance):
        self.task_instance = task_instance
        payload = self.payload = task_instance.payload
        self.timeout = payload.options['timeout']

    def execute(self):
        """
        To execute the task concurrently.
        """
        loop = asyncio.new_event_loop()
        executor = self.executor_class()
        loop.set_default_executor(executor)

        try:
            loop.run_until_complete(self._perform_execute(loop))
        except concurrent.futures.TimeoutError:
            self.shutdown(executor)
            set_status(self.task_instance.task_id, 'TIMEOUT')
        else:
            set_status(self.task_instance.task_id, 'DONE')
        finally:
            loop.close()

    async def _perform_execute(self, loop):

        future = loop.run_in_executor(
            None,
            functools.partial(self.task_instance.run, **self.payload.kwargs),
            *self.payload.args
        )
        await asyncio.wait_for(future, timeout=self.timeout, loop=loop)

    def shutdown(self, executor):
        """
        To terminate the task instance.

        Terminating a task abruptly may cause unstability, which will not be
        performed by concurrent executors while shutting down. This function
        provides graceful approach to accomplish it.
        """
        self._perform_shutdown(executor)

    def _perform_shutdown(self, executor):
        raise NotImplementedError


class ThreadExecutor(Executor):

    executor_class = concurrent.futures.ThreadPoolExecutor

    def _perform_shutdown(self, executor):
        """
        This function tries to raise an exception in the thread, in order to
        terminate it gracefully.
        """
        self.task_instance.interrupt()
        executor.shutdown(wait=True)


class ProcessExecutor(Executor):

    executor_class = concurrent.futures.ProcessPoolExecutor

    def _perform_shutdown(self, executor):
        # TODO: Too abrupt, to be improved
        for pid, process in executor._processes.items():
            process.terminate()
        executor.shutdown(wait=True)


def get_executor(task_instance):
    """
    Selects and returns a proper executor for the task instance.
    """
    return ThreadExecutor(task_instance)
