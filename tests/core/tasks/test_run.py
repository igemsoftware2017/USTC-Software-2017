import time
import subprocess

from biohub.core.tasks.storage import make_key, storage
from biohub.core.plugins import plugins, install


from ._base import TaskLiveTestCase


class Test(TaskLiveTestCase):

    def setUp(self):
        self._protect = plugins.protect(test=True, config=True)
        self._protect.acquire()

        install(['tests.core.tasks.myplugin'], update_config=True)
        subprocess.Popen(['kill', '-USR1', str(self._worker_process.pid)])\
            .communicate()

        super(Test, self).setUp()

    def tearDown(self):
        self._protect.release()

        super(Test, self).tearDown()

    def test_run(self):
        from tests.core.tasks.myplugin.tasks import MyTask

        keys = [make_key('test%d' % i) for i in range(6)]
        tasks = []

        for i in range(6):
            tasks.append(MyTask.apply_async(4, 4, keys[i]))

        for i in range(6):
            self.wait_key(keys[i], 5, 0.3, lambda v: self.assertEqual(v, 8))
            self.assertNotIn(tasks[i].status.value, ['PENDING', 'RUNNING'])

    def wait_key(self, key, rounds, duration, callback):

        for _ in range(rounds):
            time.sleep(duration)
            value = storage.get(key)

            if value is not None:
                callback(value)
                return
        else:
            raise Exception('No result found or time out.')

    def test_timeout(self):
        from tests.core.tasks.myplugin.tasks import LongTimeTask
        from biohub.core.tasks import apply_async

        key = make_key('test')

        task = apply_async(LongTimeTask, args=(key, ), timeout=2)

        self.assertIn(task.status.value, ('PENDING', 'RUNNING'))

        self.wait_key(
            key, 8, 0.5, lambda v: self.assertEqual(v, 'shutdowned'))
        self.assertEqual(task.status.value, 'TIMEOUT')

        time.sleep(1.5)

        self.assertEqual(task.status.value, 'GONE')

    def test_gone(self):

        from biohub.core.tasks import Task

        self.assertEqual(Task('23333_no_existence').status.value, 'GONE')
