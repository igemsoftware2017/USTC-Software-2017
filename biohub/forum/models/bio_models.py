from django.db import models
from django.conf import settings
from datetime import date
from django.core.validators import validate_comma_separated_integer_list
from biohub.core.files.models import File

MAX_LEN_FOR_CONTENT = 1000
MAX_LEN_FOR_THREAD_TITLE = 100
MAX_LEN_FOR_ARTICLE = 5000


class Article(models.Model):
    """
    Each article serves as one of the following: a lab record, a document or a commit object.
    The article has no 'name' field, for the name can be specified in text(using markdown)
    """
    text = models.TextField(max_length=MAX_LEN_FOR_ARTICLE)
    files = models.ManyToManyField(File)


class Brick(models.Model):
    is_part = models.BooleanField(default=True)
    name = models.CharField(max_length=100)
    # owner = models.ForeignKey(settings.AUTH_USER_MODEL,
    #                          on_delete = models.CASCADE, related_name = 'bricks_from_owner')
    designer = models.CharField(max_length=100, default='')
    group_name = models.CharField(max_length=100, default='')
    part_type = models.CharField(max_length=50, default='')  # eg: Signalling
    nickname = models.CharField(max_length=50, default='')  # eg: f1 ori

    PART_STATUS_CHOICES = (
        ('Released', 'Released'),
        ('Released HQ', 'Released HQ'),
        ('Not Released', 'Not Released'),
        ('Discontinued', 'Discontinued')
    )
    part_status = models.CharField(
        default='Not Released', max_length=15, choices=PART_STATUS_CHOICES)
    SAMPLE_STATUS_CHOICE = (
        ('Sample in Stock', 'Sample in Stock'),
        ('It\'s complicated', 'It\'s complicated'),
        ('Not in Stock', 'Not in Stock'),
        ('Informational', 'Informational')
    )
    sample_status = models.CharField(
        default='Sample in Stock', max_length=20, choices=SAMPLE_STATUS_CHOICE)
    EXPERIENCE_CHOICE = (
        ('works', 'works'),
        ('issues', 'issues'),
        ('fails', 'fails')
    )
    experience_status = models.CharField(
        default='works', max_length=8, choices=EXPERIENCE_CHOICE)
    use_num = models.PositiveIntegerField(default=0)
    twin_num = models.PositiveIntegerField(default=0)
    document = models.OneToOneField(
        Article, null=True, on_delete=models.SET_NULL, default=None)
    dna_position = models.CharField(max_length=15, validators=[
                                    validate_comma_separated_integer_list], default='')

    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='bricks_from_follower',)
    # eg: "True,False,False,True,True,True"
    assembly_compatibility = models.CharField(max_length=40, default='')
    parameters = models.TextField(default='')
    categories = models.TextField(default='')
    # private to Part:
    # a gene part has two strand, so use two fields to record the sequence.
    sequence_a = models.TextField(default='')
    sequence_b = models.TextField(default='')
    used_by = models.TextField(blank=True, default='')
    # recursive relation. the brick related must be a Device

    # private to Device
    # format: "BBa_K808013,BBa_K648028"
    sub_parts = models.TextField(blank=True, default='')
    update_time = models.DateTimeField('last updated', auto_now=True)


class Experience(models.Model):
    title = models.CharField(max_length=MAX_LEN_FOR_THREAD_TITLE)
    content = models.TextField(
        blank=True, default='', max_length=MAX_LEN_FOR_CONTENT)
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
    pub_time = models.DateField('publish time', default=date.today())
    rate = models.DecimalField(
        max_digits=2, decimal_places=1, default=0)  # eg: 3.7
    rate_num = models.IntegerField(default=0)
    # add records for users mark down who has already rated
    rate_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='experience_rated_set')
    # is_visible: no need for Experience, for the Part always exists
    # is_visible: defines whether the thread is visible to the public.
    # is_visible = models.BooleanField(default=True)
    # is_sticky = models.BooleanField(default=False)
    brick = models.ForeignKey(
        Brick, on_delete=models.CASCADE, null=True, default=None)

    class Meta:
        ordering = ('pub_time', 'id')

    def __unicode__(self):
        return '%s' % self.title

    def rate(self, rate, user):
        if user.id == self.author.id:
            return False
        if user not in self.rate_users.all():
            self.rate = (self.rate * self.rate_num + rate) / (self.rate_num + 1)
            self.rate_num += 1
            self.rate_users.add(user)
            self.save()
            return True
        return False

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
