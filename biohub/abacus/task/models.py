from django.db import models

from ..models import Abacus


class Task(models.Model):

    abacus = models.ForeignKey(
        Abacus,
        related_name='tasks')

    task_id = models.IntegerField()
    task_url = models.TextField()
    task_status = models.TextField()

    @staticmethod
    def load_by_abacus(abacus_id):
        task = Task.objects.filter(abacus_id=abacus_id)

        if task is not None:
            return task[0]

        return None
