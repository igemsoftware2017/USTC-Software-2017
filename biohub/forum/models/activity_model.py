from django.conf import settings
from django.db import models

class Activity(models.Model):
    TYPE_CHOICES = (
        ('Experience', 'Experience'),
        ('Comment', 'Comment'),
        ('Star', 'Star'),
        ('Rating', 'Rating'),
        ('Watch','Watch')
    )
    type_ = models.CharField(default='',max_length=15)
    user = models.ForeignKeyField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='activities')
    # expLink = models.
    score = models.Float
    partName
    intro