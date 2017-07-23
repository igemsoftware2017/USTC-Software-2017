from django.db import models
from django.conf import settings

MAX_LEN_FOR_ARTICLE = 5000


class File(models.Model):
    """
    Files consists of photos and other files
    """
    filepointer = models.FileField(upload_to='upload')
    description = models.TextField(max_length=100)


class Article(models.Model):
    """
    Each article serves as one of the following: a lab record, a document or a commit object. 
    The article has no 'name' field, for the name can be specified in text(using markdown)
    """
    text = models.TextField(max_length=MAX_LEN_FOR_ARTICLE)
    files = models.ManyToManyField(File)


class Part(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=250)
    description = models.TextField(blank=True, default='')
    # a gene part has two strand, so use two fields to record the sequence.
    sequence_a = models.TextField()
    sequence_b = models.TextField()
    document = models.OneToOneField(Article, on_delete=models.SET_NULL)
    lab_record = models.OneToOneField(Article, on_delete=models.SET_NULL)


class ModificationRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.SET_NULL)
    message = models.TextField(max_length=100)
    # whether the request is granted
    granted = models.BooleanField(default=False)
    commit_obj = models.OneToOneField(Article)


class Device(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    parts = models.ManyToManyField(Part)
