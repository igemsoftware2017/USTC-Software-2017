from django.db import models
from biohub.accounts.models import User
from .forummodels import Part
# Create your models here.
MAX_LEN_FOR_ARTICLE = 1000
MAX_LEN_FOR_COMMENT = 300
MAX_LEN_FOR_TITLE = 100


class Studio(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(
        blank=True, default='', max_length=MAX_LEN_FOR_ARTICLE,)
    )
    user = models.ManyToManyField(User)

class Thread(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(
        blank=True, default='', max_length=MAX_LEN_FOR_ARTICLE,)
    update_time = models.DateTimeField(
        'last updated', auto_now=True)  # 最后更新时间 auto_now使得每次更新时，将值设为现在
    pub_time = models.DateField('publish date')  # 发表时间
    # choose one from the following two.
    part = models.ForeignKey(Part, on_delete=models.CASCADE,)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE,)

    author = models.ForeignKey(User, on_delete=models.CASCADE,)


class Post(models.Model):
    content = models.TextField(
        blank=False, default='', max_length=MAX_LEN_FOR_ARTICLE,)  # 跟帖内容不能为空
    update_time = models.DateTimeField(
        'last updated', auto_now=True,)  # 最后更新时间 auto_now使得每次更新时，将值设为现在
    pub_time = models.DateField('publish date')  # 发表时间
    thread = models.ForeignKey(
        Thread, on_delete=models.SET_NULL,)  # 目前设计：跟帖不能轻易随题主而删去
    author = models.ForeignKey(User, on_delete=models.CASCADE,)


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.SET_NULL,
    )
    content = models.TextField(blank=False, max_length=MAX_LEN_FOR_COMMENT)
    author = models.ForeignKey(User, on_delete=models.CASCADE,)
    pub_time = models.DateField('publish date')  # 发表时间



