import decimal
from datetime import date

from django.conf import settings
from django.db import models, transaction

from biohub.core.files.models import File
from biohub.forum.user_defined_signals import rating_brick_signal, \
    up_voting_experience_signal, watching_brick_signal


MAX_LEN_FOR_CONTENT = 1000
MAX_LEN_FOR_THREAD_TITLE = 100
MAX_LEN_FOR_ARTICLE = 5000


class Article(models.Model):
    """
    Each article serves as one of the following: a lab experience, or a document.
    The article has no 'name' field, for the name can be specified in text(using markdown)
    """
    text = models.TextField(max_length=MAX_LEN_FOR_ARTICLE)
    files = models.ManyToManyField(File, default=None)


class Brick(models.Model):
    # is_part = models.BooleanField(default=True)
    # no need. can be telled from 'sub_parts'
    name = models.CharField(max_length=200, unique=True)
    # owner = models.ForeignKey(settings.AUTH_USER_MODEL,
    #                          on_delete = models.CASCADE, related_name = 'bricks_from_owner')
    designer = models.CharField(max_length=200, default='')
    group_name = models.CharField(max_length=200, default='')
    part_type = models.CharField(max_length=100, default='')  # eg: Signalling
    nickname = models.CharField(max_length=100, default='')  # eg: f1 ori

    # PART_STATUS_CHOICES = (
    #     ('Released', 'Released'),
    #     ('Released HQ', 'Released HQ'),
    #     ('Not Released', 'Not Released'),
    #     ('Discontinued', 'Discontinued')
    # )
    part_status = models.CharField(
        default='Not Released', max_length=50)
    # SAMPLE_STATUS_CHOICE = (
    #     ('Sample in Stock', 'Sample in Stock'),
    #     ('It\'s complicated', 'It\'s complicated'),
    #     ('Not in Stock', 'Not in Stock'),
    #     ('Informational', 'Informational')
    # )
    sample_status = models.CharField(
        default='Sample in Stock', max_length=50)
    # EXPERIENCE_CHOICE = (
    #     ('works', 'works'),
    #     ('issues', 'issues'),
    #     ('fails', 'fails')
    # )
    experience_status = models.CharField(
        default='works', max_length=50)
    use_num = models.PositiveIntegerField(default=0)
    twin_num = models.PositiveIntegerField(default=0)
    document = models.OneToOneField(
        Article, null=True, on_delete=models.SET_NULL, default=None)
    # dna position is already included in seqFeatures
    # dna_position = models.CharField(max_length=15, validators=[
    #                                 validate_comma_separated_integer_list], default='')

    watch_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='bricks_watched',
    )
    # eg: "True,False,False,True,True,True"
    assembly_compatibility = models.CharField(max_length=40, default='')
    parameters = models.TextField(default='')
    categories = models.TextField(default='')
    # private to Part:
    # a gene part has two strand, so use two fields to record the sequence.
    sequence_a = models.TextField(default='')
    sequence_b = models.TextField(default='')
    # used_by = models.TextField(blank=True, default='') # temporarily removed
    # recursive relation. the brick related must be a Device

    # private to Device
    # format: "BBa_K808013,BBa_K648028"
    sub_parts = models.TextField(blank=True, default='', null=True)
    update_time = models.DateTimeField('last updated', auto_now=True)

    rate_score = models.DecimalField(
        max_digits=2, decimal_places=1, default=0)  # eg: 3.7
    rate_num = models.IntegerField(default=0)
    # add records for users mark down who has already rated
    rate_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='bricks_rated')
    star_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='bricks_starred')
    stars = models.PositiveIntegerField(default=0)

    def watch(self, user):
        if not self.watch_users.filter(pk=user.id).exists():
            with transaction.atomic():
                self.watch_users.add(user)
                watching_brick_signal.send(sender=self.__class__, instance=self, user=user)
                return True
        return False

    def cancel_watch(self, user):
        if self.watch_users.filter(pk=user.id).exists():
            self.watch_users.remove(user)
            return True
        return False

    def star(self, user):
        if not self.star_users.filter(pk=user.id).exists():
            with transaction.atomic():
                self.star_users.add(user)
                self.stars += 1
                self.save()

            return True

        return False

    def unstar(self, user):
        if self.star_users.filter(pk=user.id).exists():
            self.star_users.remove(user)
            self.stars -= 1
            self.save()

            return True

        return False

    def rate(self, rate, user):
        if not self.rate_users.filter(pk=user.id).exists():
            with transaction.atomic():
                self.rate_score = (self.rate_score *
                                   self.rate_num + decimal.Decimal(rate)) / (self.rate_num + 1)
                self.rate_num += 1
                self.rate_users.add(user)
                self.save()
                rating_brick_signal.send(sender=self.__class__, user_rating=user, instance=self,
                                         rating_score=rate, curr_score=self.rate_score)
            return True
        return False


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
    update_time = models.DateTimeField(
        'last updated', auto_now=True)
    # Automatically set the pub_time to now when the object is first created.
    # Also the pub_time can be set manually.
    pub_time = models.DateField('publish time', default=date.today)
    # is_visible: no need for Experience, for the Part always exists
    # is_visible: defines whether the thread is visible to the public.
    # is_visible = models.BooleanField(default=True)
    # is_sticky = models.BooleanField(default=False)
    brick = models.ForeignKey(
        Brick, on_delete=models.CASCADE, null=True, default=None)
    up_vote_num = models.IntegerField(default=0)
    # add records for users mark down who has already voted for the post
    up_vote_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='experiences_voted')

    def up_vote(self, user):
        if self.author is not None and self.author.id == user.id:
            return False
        if not self.up_vote_users.filter(pk=user.id).exists():
            with transaction.atomic():
                self.up_vote_num += 1
                self.up_vote_users.add(user)
                self.save()
                up_voting_experience_signal.send(sender=self.__class__, instance=self,
                                                 user_up_voting=user, curr_up_vote_num=self.up_vote_num)
            return True
        return False

    def cancel_up_vote(self, user):
        if self.up_vote_users.filter(pk=user.id).exists():
            with transaction.atomic():
                self.up_vote_users.remove(user)
                self.up_vote_num -= 1
                self.save()
            return True
        return False

    class Meta:
        ordering = ('pub_time', 'id')

    def __unicode__(self):
        return '%s' % self.title

    # def hide(self):
    #     self.is_visible = False
    #     self.save()
    #     for post in self.post_set.all():
    #         post.hide()

    # def show(self):
    #     self.is_visible = True
    #     self.save()
    #     for post in self.post_set.all():
    #         post.show()

    # Warning: Because all comments are also posts,
    # please use the methods below to get posts directly attached to the thread.
    # When using t.post_set.all/filter/get, you will also get the comments.
    # def get_post_set_all(self):
    #     return self.post_set.filter(is_comment=False)
    #
    # def get_post_set_filter(self, *args, **kwargs):
    #     return self.post_set.filter(is_comment=False, *args, **kwargs)
    #
    # def get_post_set_by(self, *args, **kwargs):
    #     return self.post_set.get(is_comment=False, *args, **kwargs)


class SeqFeature(models.Model):
    brick = models.ForeignKey(
        Brick, on_delete=models.CASCADE, related_name='seqFeatures')
    feature_type = models.CharField(max_length=15, default='')
    start_loc = models.PositiveIntegerField(default=0)
    end_loc = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=15, default='')
    reserve = models.BooleanField(default=False)
    update_time = models.DateTimeField('last updated', auto_now=True)


# class ModificationRequest(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL,
#                              on_delete=models.CASCADE)
#     brick = models.ForeignKey(Brick, on_delete=models.SET_NULL, null=True)
#     message = models.TextField(max_length=100)
#     # whether the request is granted
#     granted = models.BooleanField(default=False)
#     commit_obj = models.OneToOneField(Article)
#     #
#     submit_time = models.DateTimeField(auto_now_add=True)
#     # set to time when it's granted by the author
#     accept_time = models.DateTimeField()
