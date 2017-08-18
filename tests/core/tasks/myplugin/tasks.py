import time

from biohub.core.tasks import Task
from biohub.core.tasks.storage import storage


class MyTask(Task):

    def run(self, a, b, key):
        storage.set(key, a + b)


class LongTimeTask(Task):

    def run(self, key):
        self._key = key

        while True:
            time.sleep(0.5)
            self.check_interrupt()

    def before_interrupt(self):
        storage.set(self._key, 'shutdowned')
