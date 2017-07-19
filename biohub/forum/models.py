from django.db import models
from biohub.accounts.models import User
# Create your models here.
MAX_LEN_FOR_POST = 1000
MAX_LEN_FOR_COMMENT = 300


class Thread(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(
        blank=True, default='', max_length=MAX_LEN_FOR_POST,)
    author = models.ForeignKey(User, on_delete=models.CASCADE,)
    update_time = models.DateTimeField(
        'last updated', auto_now=True)  # 最后更新时间 auto_now使得每次更新时，将值设为现在
    pub_time = models.DateField('publish date')  # 发表时间


class Post(models.Model):
    thread = models.ForeignKey(
        Thread, on_delete=models.SET_NULL,)  # 目前设计：跟帖不能轻易随题主而删去
    content = models.TextField(
        blank=False, default='', max_length=MAX_LEN_FOR_POST,)  # 跟帖内容不能为空
    author = models.ForeignKey(User, on_delete=models.CASCADE,)
    update_time = models.DateTimeField(
        'last updated', auto_now=True,)  # 最后更新时间 auto_now使得每次更新时，将值设为现在
    pub_time = models.DateField('publish date')  # 发表时间


class Comment(models.Model):
    thread = models.ForeignKey(
        Post, on_delete=models.SET_NULL,
    )
    content = models.TextField(blank=False, max_length=MAX_LEN_FOR_COMMENT)
    author = models.ForeignKey(User, on_delete=models.CASCADE,)
    pub_time = models.DateField('publish date')  # 发表时间

