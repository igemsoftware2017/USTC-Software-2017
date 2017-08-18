from ._base import TaskTestCase


class Test(TaskTestCase):

    def test_register(self):
        from biohub.core.tasks import Task, tasks

        class MyTask(Task):

            def run(self):
                pass

        self.assertEqual(1, len(tasks.mapping))

    def test_base_class_excluded(self):
        from biohub.core.tasks import Task

        self.assertNotIn(Task, self._tasks_registry_mapping.values())

    def test_duplicate(self):
        from biohub.core.tasks import Task
        from biohub.core.tasks.exceptions import TaskRegistered

        class MyTask(Task):
            pass

        with self.assertRaises(TaskRegistered):
            class MyTask(Task):  # noqa
                pass
