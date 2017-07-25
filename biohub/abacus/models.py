from django.db import models
from django.conf import settings


class Abacus(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='abacus')

    tag = models.TextField(max_length=255)

    # upload_file = models.FileField(upload_to=AbacusConfig.upload_path)
    # download_file = models.FileField()
    descriable = models.TextField(max_length=255)
    create_date = models.TimeField(auto_now_add=True, db_index=True)
    shared = models.BooleanField(default=False)

    # -1:error,0-to be start,1-processing,2-done
    status = models.IntegerField()

    class Meta:
        ordering = {'-create_date', }
