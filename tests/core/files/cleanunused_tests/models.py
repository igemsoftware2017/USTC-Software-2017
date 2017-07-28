from django.db import models


class TestModel(models.Model):

    text = models.TextField()

    class Meta:
        app_label = 'cleanunused_tests'
