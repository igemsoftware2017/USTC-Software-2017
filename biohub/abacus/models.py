from django.db import models
from django.conf import settings


class Abacus(models.Model):

    ERROR = -1
    TO_BE_START = 0
    UPLOADED = 1
    QUEUING = 2
    PROCESSING = 3
    FINISHED = 4

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='abacus')

    tag = models.TextField(default="", max_length=255)

    descriable = models.TextField(default="", max_length=255)
    create_date = models.DateTimeField(auto_now_add=True, db_index=True)
    shared = models.BooleanField(default=False)

    status = models.IntegerField()

    @staticmethod
    def load(id):
        abacus = Abacus.objects.filter(id=id)

        if len(abacus) == 0:
            return None

        return abacus[0]

    class Meta:
        ordering = ('-create_date', )

