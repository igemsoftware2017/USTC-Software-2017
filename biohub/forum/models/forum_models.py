from django.db import models
from django.conf import settings

from .bio_models import Brick

MAX_LEN_FOR_CONTENT = 1000
MAX_LEN_FOR_THREAD_TITLE = 100


class Studio(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(
        blank=True, default='', max_length=1000,)
    # Warning: a user should either be added to users or saved as an administrator.
    # Don't add it to both.
    # Note: the founder of the studio should be the administrator.
    # Warning: creating a studio, an administrator should also be saved.
    # Or the studio will be treated as an empty studio and will be deleted.
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='studios_from_user')
    administrator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                      null=True, related_name='studios_from_admin')


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
    # Deleting a studio or the bio-brick, the threads won't be truly deleted. But they will hide.
    brick = models.ForeignKey(Brick, on_delete=models.SET_NULL, null=True, default=None)
    studio = models.ForeignKey(Studio, on_delete=models.SET_NULL, null=True, default=None)

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

    # Warning: Because all comments are also posts,
    # please use the methods below to get posts directly attached to the thread.
    # When using t.post_set.all/filter/get, you will also get the comments.
    def get_post_set_all(self):
        return self.post_set.filter(is_comment=False)

    def get_post_set_filter(self, *args, **kwargs):
        return self.post_set.filter(is_comment=False, *args, **kwargs)

    def get_post_set_by(self, *args, **kwargs):
        return self.post_set.get(is_comment=False, *args, **kwargs)


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
    # No need to explicitly specify is_comment. It will be added automaticallly.
    is_comment = models.BooleanField()

    def __init__(self, *args, **kwargs):
        if 'is_comment' not in kwargs:
            kwargs['is_comment'] = False
        super(Post, self).__init__(*args, **kwargs)

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
    reply_to = models.ForeignKey(
        Post, on_delete=models.SET_NULL, null=True, related_name='comments'
    )

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(is_comment=True, *args, **kwargs)
