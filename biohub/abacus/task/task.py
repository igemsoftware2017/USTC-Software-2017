from biohub.abacus import util
from .models import Abacus
from .models import Task
from ..task import request_tool


def create_task(abacus):
    task = Task()
    task.abacus = abacus
    request_tool.post_task(task, abacus)

def get_status_by_task(task):
    return request_tool.get_task_status(task)

def get_status_by_abacus(abacus):
    task = Task.objects.filter(abacus=abacus)
    if task is None:
        return 'ERROR'
    return get_status_by_task(task)