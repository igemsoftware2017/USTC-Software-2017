from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation

from .bio_models import Experience


MAX_LEN_FOR_CONTENT = 1000


class Post(models.Model):
    # when the experience is deleted, the posts attached to it won't be deleted.
    # The is_visible fields of those posts will be set False instead.
    # That is, they can't be read by the people except the author himself.
    experience = models.ForeignKey(
        Experience, on_delete=models.CASCADE, null=True, related_name='posts')
    content = models.TextField(blank=False, max_length=MAX_LEN_FOR_CONTENT, )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    update_time = models.DateTimeField(
        'last updated', auto_now=True,)
    pub_time = models.DateTimeField('publish time', auto_now_add=True)
    is_visible = models.BooleanField(default=True)

    activities = GenericRelation('forum.Activity', 'target_id', 'target_type', related_query_name='post')
    notices = GenericRelation('notices.Notice', 'target_id', 'target_type', related_query_name='post')

    class Meta:
        ordering = ['-pub_time']

    def hide(self):
        self.is_visible = False
        self.save()

    def show(self):
        self.is_visible = True
        self.save()

    def get_router_arguments(self):
        return 'post', self.pk
