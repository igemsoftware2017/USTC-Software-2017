from django.db import models


class TestModel(models.Model):

    field_a = models.CharField(max_length=80)
