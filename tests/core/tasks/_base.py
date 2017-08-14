from unittest import skipIf
from weakref import WeakValueDictionary

from django.test import TestCase

from channels.test import ChannelLiveServerTestCase

from biohub.utils.detect import features


@skipIf(not features.redis, 'Task tests require redis.')
class TaskTestCase(TestCase):

    def setUp(self):
        from biohub.core.tasks import tasks, storage

        # Store registry
        self._tasks_registry_mapping = tasks.mapping
        tasks.mapping = WeakValueDictionary()

        storage.clear_keys()

    def tearDown(self):
        from biohub.core.tasks import tasks, storage

        # Restore registry
        tasks.mapping = self._tasks_registry_mapping

        # Restore cache prefix
        storage.clear_keys()


class TaskLiveTestCase(TaskTestCase, ChannelLiveServerTestCase):
    pass
