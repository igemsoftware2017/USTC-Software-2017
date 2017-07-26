from django.db import models
from django.conf import settings

import datetime


class Abacus(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='abacus')

    tag = models.TextField(default="", max_length=255)

    descriable = models.TextField(default="", max_length=255)
    create_date = models.DateTimeField(auto_now_add=True, db_index=True)
    shared = models.BooleanField(default=False)

    # -1:error,0-to be start,1-uploaded and queuing,2-processing,3-done
    status = models.IntegerField()

    class Meta:
        ordering = ('-create_date', )
