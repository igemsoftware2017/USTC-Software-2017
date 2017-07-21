from django.db import models


class Part(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=250)
    description = models.TextField(blank=True, default='')
    # a gene part has two strand, so use two fields to record the sequence.
    sequence_a = models.TextField()
    sequence_b = models.TextField()
