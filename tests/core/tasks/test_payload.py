from biohub.core.tasks.payload import TaskPayload
from biohub.core.tasks.exceptions import TaskInstanceNotExists

from ._base import TaskTestCase

raw_data = ('Task', 'Task-sadsgadsga', ['6', '8', 6.7, 1 + 4j],
            dict(a=dict(b=5)), dict(process=True, timeout=180))


def payload_to_tuple(payload):
    return payload.task_name, payload.task_id, payload.args, payload.kwargs, payload.options  # noqa


class Test(TaskTestCase):

    def test_pack_data(self):
        packed_data = TaskPayload(*raw_data).packed_data

        self.assertSequenceEqual(
            raw_data,
            payload_to_tuple(
                TaskPayload.from_packed_data(packed_data)
            )
        )

    def test_store_and_get(self):
        TaskPayload(*raw_data).store()

        self.assertSequenceEqual(
            raw_data,
            payload_to_tuple(
                TaskPayload.from_task_id(raw_data[1])
            )
        )

    def test_get_failure(self):
        with self.assertRaises(TaskInstanceNotExists):
            TaskPayload.from_task_id(raw_data[1])
