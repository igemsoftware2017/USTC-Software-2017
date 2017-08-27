from django.db import models
from django.conf import settings

from .bio_models import Experience


MAX_LEN_FOR_CONTENT = 1000

# class Studio(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     description = models.TextField(
#         blank=True, default='', max_length=1000,)
#     # Warning: a user should either be added to users or saved as an administrator.
#     # Don't add it to both.
#     # Note: the founder of the studio should be the administrator.
#     # Warning: creating a studio, an administrator should also be saved.
#     # Or the studio will be treated as an empty studio and will be deleted.
#     users = models.ManyToManyField(
#         settings.AUTH_USER_MODEL, related_name='studios_from_user')
#     administrator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
#                                       null=True, related_name='studios_from_admin')


class Post(models.Model):
    # when the experience is deleted, the posts attached to it won't be deleted.
    # The is_visible fields of those posts will be set False instead.
    # That is, they can't be read by the people except the author himself.
    experience = models.ForeignKey(
        Experience, on_delete=models.SET_NULL, null=True)
    content = models.TextField(blank=False, max_length=MAX_LEN_FOR_CONTENT, )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_set')
    update_time = models.DateTimeField(
        'last updated', auto_now=True,)
    pub_time = models.DateTimeField('publish time', auto_now_add=True)
    # down_vote_num = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    # No need to explicitly specify is_comment. It will be added automatically.
    # There's only one level of replies
    # is_comment = models.BooleanField()

    class Meta:
        ordering = ['pub_time']

    # def __init__(self, *args, **kwargs):
    #     if 'is_comment' not in kwargs:
    #         kwargs['is_comment'] = False
    #     super(Post, self).__init__(*args, **kwargs)

    def hide(self):
        self.is_visible = False
        self.save()
        # for comment in self.comments.all():
        #     comment.hide()

    def show(self):
        self.is_visible = True
        self.save()
        # for comment in self.comments.all():
        #     comment.show()

# # Inherit Post to support comments of comments.
# class Comment(Post):
#     # Like Post, the comment won't be truly deleted if the post is deleted.
#     # Note: relate_name is set, please use post.comments.all() rather than post.comment_set.all()
#     reply_to = models.ForeignKey(
#         Post, on_delete=models.SET_NULL, null=True, related_name='comments'
#     )

#     def __init__(self, *args, **kwargs):
#         super(Comment, self).__init__(is_comment=True, *args, **kwargs)


# class Invitation(models.Model):
#     sender = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invitations_from_sender')
#     receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
#                                  null=True, related_name='invitations_from_receiver')
#     studio = models.ForeignKey(Studio, on_delete=models.SET_NULL, null=True)
#     agreed = models.BooleanField(default=False)
