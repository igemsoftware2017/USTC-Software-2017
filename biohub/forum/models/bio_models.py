from datetime import date

from django.conf import settings
from django.db import models, transaction

from biohub.core.files.models import File
from biohub.forum.user_defined_signals import up_voting_experience_signal


MAX_LEN_FOR_THREAD_TITLE = 500


class Article(models.Model):
    """
    Each article serves as one of the following: a lab experience, or a document.
    The article has no 'name' field, for the name can be specified in text(using markdown)
    """
    text = models.TextField()
    digest = models.TextField(blank=True, null=False)
    files = models.ManyToManyField(File, default=None)

    def make_digest(self):
        import re
        string = self.text.replace('\n', ' ')
        string = re.sub(r'\!?\[(.*?)\]\(.+?\)', r'\1', string)
        string = re.sub(r'[^a-zA-Z\d\-_\(\)]+', ' ', string)

        self.digest = string[:string.rfind(' ', 0, 600)]
        return self.digest

    def save(self, *args, **kwargs):
        self.make_digest()

        super(Article, self).save(*args, **kwargs)


class ExperienceQuerySet(models.QuerySet):

    def with_posts_num(self):
        return self.annotate(
            posts_num=models.Count('posts')
        )

    def with_voted_flag(self, user):
        return self.annotate(
            voted=models.Exists(
                Experience.voted_users.through.objects.filter(
                    user=user.id,
                    experience=models.OuterRef('pk')
                )
            )
        )


class Experience(models.Model):
    # In fact, a brick's experience consists not only user reviews,
    # but also applications of the brick.
    # This class only contains user reviews

    # According to iGem's websites, a user review has no title. We can make this optional.
    title = models.CharField(max_length=MAX_LEN_FOR_THREAD_TITLE, blank=True, default='')
    # experience can be uploaded by users, so use Article to support markdown.
    content = models.OneToOneField(
        Article, null=True, on_delete=models.SET_NULL, default=None)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='experience_set',
        null=True, default=None
    )
    # If the experience was uploaded by a user, the field author_name will be the username,
    # If the experience was fetched from the iGEM website,
    # the author_name should be set according to the data fetched.
    author_name = models.CharField(max_length=100, blank=True, default='')
    last_fetched = models.DateTimeField('last updated', null=True, default=None)
    # Automatically set the pub_time to now when the object is first created.
    # Also the pub_time can be set manually.
    pub_time = models.DateTimeField('publish time', auto_now_add=True)
    brick = models.ForeignKey(
        'biobrick.BiobrickMeta', on_delete=models.CASCADE, null=True, default=None,
        related_name='experiences')
    votes = models.IntegerField(default=0)
    # add records for users mark down who has already voted for the post
    voted_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='experiences_voted'
    )

    objects = ExperienceQuerySet.as_manager()

    def vote(self, user):
        if self.author is not None and self.author.id == user.id:
            return False
        if not self.voted_users.filter(pk=user.id).exists():
            with transaction.atomic():
                self.votes += 1
                self.voted_users.add(user)
                self.save(update_fields=['votes'])
                up_voting_experience_signal.send(
                    sender=self.__class__, instance=self,
                    user_up_voting=user, curr_up_vote_num=self.votes)
            return True
        return False

    def unvote(self, user):
        if self.voted_users.filter(pk=user.id).exists():
            with transaction.atomic():
                self.voted_users.remove(user)
                self.votes -= 1
                self.save()
            return True
        return False

    class Meta:
        ordering = ('-pub_time', 'id')

    def __str__(self):
        return '%s' % self.title
