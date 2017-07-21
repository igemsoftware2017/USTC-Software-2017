from django.db import models
from django.conf import settings

MAX_LEN_FOR_POST_CONTENT = 1000
MAX_LEN_FOR_COMMENT_CONTENT = 300
MAX_LEN_FOR_THREAD_TITLE = 100


class Thread(models.Model):
    title = models.CharField(max_length=MAX_LEN_FOR_THREAD_TITLE)
    content = models.TextField(
        blank=True, default='', max_length=MAX_LEN_FOR_POST_CONTENT,)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    # update_time: The time the thread is updated by its author.
    # It should be set to the current time automatically.
    update_time = models.DateTimeField(
        'last updated', auto_now=True)
    # last_post_time: The time the last reply is posted.
    last_post_time = models.DateTimeField('time of last reply', null=True)
    # post_num: the number of the replies posted.
    post_num = models.IntegerField(default=0)
    # Automatically set the pub_time to now when the object is first created.
    pub_time = models.DateField('publish date', auto_now_add=True)
    # is_visible: defines whether the thread is visible to the public.
    is_visible = models.BooleanField(default=True)


class Post(models.Model):
    # when the thread is deleted, the posts attached to it won't be deleted.
    # The is_visible fields of those posts will be set False instead.
    # That is, they can't be read by the people except the author himself.
    thread = models.ForeignKey(
        Thread, on_delete=models.SET_NULL, null=True)
    content = models.TextField(blank=False, max_length=MAX_LEN_FOR_POST_CONTENT,)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    update_time = models.DateTimeField(
        'last updated', auto_now=True,)
    pub_time = models.DateField('publish date', auto_now_add=True)
    up_vote_num = models.IntegerField(default=0)
    down_vote_num = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)


# Inherit Post to support comments of comments.
class Comment(Post):
    # Like Post, the comment won't be truly deleted if the post is deleted.
    post = models.ForeignKey(
        Post, on_delete=models.SET_NULL, null=True
    )
    content = models.TextField(blank=False, max_length=MAX_LEN_FOR_COMMENT_CONTENT)
