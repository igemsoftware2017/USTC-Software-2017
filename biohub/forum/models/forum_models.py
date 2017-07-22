from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_delete

from .bio_models import Part

MAX_LEN_FOR_CONTENT = 1000
MAX_LEN_FOR_THREAD_TITLE = 100


class Studio(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(
        blank=True, default='', max_length=1000,)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)


class Thread(models.Model):
    title = models.CharField(max_length=MAX_LEN_FOR_THREAD_TITLE)
    content = models.TextField(
        blank=True, default='', max_length=MAX_LEN_FOR_CONTENT)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    update_time = models.DateTimeField(
        'last updated', auto_now=True)
    # Automatically set the pub_time to now when the object is first created.
    pub_time = models.DateField('publish date', auto_now_add=True)
    # is_visible: defines whether the thread is visible to the public.
    is_visible = models.BooleanField(default=True)
    is_sticky = models.BooleanField(default=False)
    # choose one from the following two.
    # Though the two field's default value are both None, one of them must be provided values.
    # TODO: add check in serializers to make sure one of them (and only one of them) has values. \
    # Or, can we check in models?
    part = models.ForeignKey(Part, on_delete=models.CASCADE, null=True, default=None)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, null=True, default=None)

    def hide(self):
        self.is_visible = False
        self.save()
        for post in self.post_set.all():
            post.hide()

    def show(self):
        self.is_visible = True
        self.save()
        for post in self.post_set.all():
            post.show()


class Post(models.Model):
    # when the thread is deleted, the posts attached to it won't be deleted.
    # The is_visible fields of those posts will be set False instead.
    # That is, they can't be read by the people except the author himself.
    thread = models.ForeignKey(
        Thread, on_delete=models.SET_NULL, null=True)
    content = models.TextField(blank=False, max_length=MAX_LEN_FOR_CONTENT, )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    update_time = models.DateTimeField(
        'last updated', auto_now=True,)
    pub_time = models.DateField('publish date', auto_now_add=True)
    up_vote_num = models.IntegerField(default=0)
    down_vote_num = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    def hide(self):
        self.is_visible = False
        self.save()
        for comment in self.comments.all():
            comment.hide()

    def show(self):
        self.is_visible = True
        self.save()
        for comment in self.comments.all():
            comment.show()


# Inherit Post to support comments of comments.
class Comment(Post):
    # Like Post, the comment won't be truly deleted if the post is deleted.
    # Note: relate_name is set, please use post.comments.all() rather than post.comment_set.all()
    post = models.ForeignKey(
        Post, on_delete=models.SET_NULL, null=True, related_name='comments'
    )


@receiver(pre_delete, sender=Thread)
def hide_attached_posts(instance, **kwargs):
    for post in instance.post_set.all():
        post.hide()


@receiver(pre_delete, sender=Post)
def hide_attached_comments(instance, **kwargs):
    for comment in instance.comments.all():
        comment.hide()
