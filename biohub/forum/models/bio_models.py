from django.db import models
from django.conf import settings

MAX_LEN_FOR_ARTICLE = 5000


class File(models.Model):
    """
    Files consists of photos and other files
    """
    filepointer = models.FileField(upload_to='upload')
    description = models.TextField(max_length=100)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    # 'users' field is a must.
    # Because files may be included to users' media repository, or may not(set to NULL)


class Article(models.Model):
    """
    Each article serves as one of the following: a lab record, a document or a commit object. 
    The article has no 'name' field, for the name can be specified in text(using markdown)
    """
    text = models.TextField(max_length=MAX_LEN_FOR_ARTICLE)
    files = models.ManyToManyField(File)


class Brick(models.Model):
    ispart = models.BooleanField(default=True)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL)
    description = models.TextField(blank=True, default='')
    document = models.OneToOneField(Article, on_delete=models.SET_NULL,
                                    null=True, related_name='brick_from_doc')
    lab_record = models.OneToOneField(Article, on_delete=models.SET_NULL,
                                      null=True, related_name='brick_from_record')
    # private to Part:
    # a gene part has two strand, so use two fields to record the sequence.
    sequence_a = models.TextField()
    sequence_b = models.TextField()
    type = models.CharField(max_length=250)
    internal_part_to = models.ForeignKey(
        'self', on_delete=models.SET_NULL, related_name='internal_parts')
    # recursive relation. the brick related must be a Device

    # private to Device
    # format: "BBa_K808013,BBa_K648028"
    external_parts = models.TextField(blank=True, default='')


class ModificationRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    brick = models.ForeignKey(Brick, on_delete=models.SET_NULL, null=True)
    message = models.TextField(max_length=100)
    # whether the request is granted
    granted = models.BooleanField(default=False)
    commit_obj = models.OneToOneField(Article)
    # TODO: add TimeField
    submit_time = models.DateTimeField(auto_now_add=True)
    accept_time = models.DateTimeField() #set to time when it's granted by the author