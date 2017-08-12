from django.conf import settings
from django.db import models


class ActivityParam(models.Model):
    type = models.CharField(default='', max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    expLink = models.CharField(default='',blank=True,max_length=100)
    score = models.DecimalField(
        max_digits=2, decimal_places=1, default=0)  # eg: 3.7
    partName = models.CharField(default='', max_length=15)
    intro = models.CharField(default='', blank=True, max_length=50)


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
    params = models.OneToOneField(ActivityParam, null=True, on_delete=models.CASCADE)
