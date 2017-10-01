from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey

from biohub.utils.db import PackedField


class Activity(models.Model):
    TYPE_CHOICES = (
        ('Experience', 'Experience'),
        ('Comment', 'Comment'),
        ('Star', 'Star'),
        ('Rating', 'Rating'),
        ('Watch', 'Watch')
    )
    type = models.CharField(default='', max_length=15)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='activities')
    brick_name = models.CharField(max_length=20)
    params = PackedField()
    acttime = models.DateTimeField(auto_now_add=True)

    target_type = models.ForeignKey('contenttypes.ContentType', null=True)
    target_id = models.PositiveSmallIntegerField(default=0, null=True)

    target = GenericForeignKey('target_type', 'target_id')
