import decimal
import datetime

from django.utils import timezone
from django.db import models, transaction

from biohub.accounts.models import User
from biohub.utils.db import PackedField
from biohub.forum.user_defined_signals import rating_brick_signal, \
    watching_brick_signal, unwatching_brick_signal


class WatchingUser(models.Model):

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    brick = models.ForeignKey('BiobrickMeta', on_delete=models.CASCADE)


class StarredUser(models.Model):

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    brick = models.ForeignKey('BiobrickMeta', on_delete=models.CASCADE)


class RatedUser(models.Model):

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    brick = models.ForeignKey('BiobrickMeta', on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=2, decimal_places=1, default=0)


class WeightBase(models.Model):

    weight = models.FloatField(default=0.0)
    weight_updated_time = models.DateTimeField(null=True)

    class Meta:
        abstract = True


class BiobrickWeight(WeightBase):

    part_name = models.CharField(max_length=255, db_index=True, null=False, primary_key=True)


class MetaBase(models.Model):

    UPDATE_DELTA = datetime.timedelta(days=10)
    SHARED_FIELDS = (
        'part_type', 'author', 'part_status', 'sample_status', 'uses'
    )

    part_type = models.CharField(max_length=20, null=True, blank=True)
    author = models.CharField(max_length=200, null=True, blank=True)
    part_status = models.CharField(max_length=40, null=True)
    sample_status = models.CharField(max_length=40, null=True)
    uses = models.IntegerField(null=True, default=-1)  # essential, ordering

    group_name = models.CharField(max_length=200, default='')
    experience_status = models.CharField(default='works', max_length=50)
    twin_num = models.PositiveIntegerField(default=0)

    parameters = PackedField(default='')

    rates = models.PositiveIntegerField(default=0)
    rate_score = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    stars = models.PositiveIntegerField(default=0)
    watches = models.PositiveIntegerField(default=0)

    last_fetched = models.DateTimeField(null=True, default=None)

    class Meta:
        abstract = True

    @property
    def meta_exists(self):
        return self.group_name is not None

    @property
    def should_fetch(self):
        return self.last_fetched is None or timezone.now() - self.last_fetched > self.UPDATE_DELTA

    def fetch(self):
        from .spiders import BrickSpider, ExperienceSpider

        BrickSpider().fill_from_page(self)
        ExperienceSpider().fill_from_page(self.part_name)
        self.refresh_from_db()


class BiobrickMeta(MetaBase):

    part_name = models.CharField(max_length=255, db_index=True, null=False, primary_key=True)

    users_watching = models.ManyToManyField('accounts.User', related_name='bricks_watching', through=WatchingUser)
    users_rated = models.ManyToManyField('accounts.User', related_name='bricks_rated', through=RatedUser)
    users_starred = models.ManyToManyField('accounts.User', related_name='bricks_starred', through=StarredUser)

    document = models.OneToOneField(
        'forum.Article',
        null=True,
        on_delete=models.SET_NULL,
        default=None
    )

    def save(self, fill_shared_fields=False, *args, **kwargs):

        if fill_shared_fields:
            part = Part.objects.only(*self.SHARED_FIELDS).get(part_name=self.part_name)

            for field in self.SHARED_FIELDS:
                setattr(self, field, getattr(part, field))

        return super(BiobrickMeta, self).save(*args, **kwargs)


def _related_user_queryset(through_class, instance):

    return User.objects.filter(
        pk__in=models.Subquery(
            through_class.objects.filter(brick=instance.part_name).values('user')
        )
    )


class Biobrick(MetaBase, WeightBase):
    # The official model of biobrick from parts.igem.org
    part_id = models.AutoField(primary_key=True)  # essential
    ok = models.NullBooleanField(default=True)  # essential, ordering
    part_name = models.CharField(max_length=255, null=True, blank=True)  # essential, filtering
    short_desc = models.CharField(max_length=100, null=True, blank=True)  # essential, filtering
    description = models.TextField(null=True, blank=True)  # essential, filtering

    # no references
    # owning_group_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)  # essential, filtering
    dominant = models.NullBooleanField(default=False)  # essential, ordering, 01 field
    # 01 field with no value for part with 1 is too few
    # informational = models.NullBooleanField(default=False)

    # foreign key
    # discontinued = models.IntegerField(null=True, default=0)
    # part_status = models.CharField(max_length=40, null=True)  # essential
    # sample_status = models.CharField(max_length=40, null=True)  # essential, ordering, filtering

    # p_status_cache = models.CharField(max_length=1000, null=True)
    # s_status_cache = models.CharField(max_length=1000, null=True)

    creation_date = models.DateField(null=True, blank=True)  # essential

    # modification related, ignored
    # m_datetime = models.DateTimeField(null=True, blank=True)
    # m_user_id = models.IntegerField(null=True, default=0)

    # doc_size = models.IntegerField(null=True, default=0)  # ordering
    works = models.CharField(max_length=10, null=False)  # ordering
    favorite = models.IntegerField(null=True, default=0)  # ordering

    # no reference
    # specified_u_list = models.TextField(null=True, blank=True)
    # deep_u_list = models.TextField(null=True, blank=True)
    # deep_count = models.IntegerField(null=True, blank=True)
    # ps_string = models.TextField(null=True, blank=True)
    # scars = models.CharField(max_length=20, null=True, default='10')
    # default_scars = models.CharField(max_length=20, null=False, default='10')
    # owner_id = models.IntegerField(null=True, blank=True)
    # group_u_list = models.TextField(null=True, blank=True)
    has_barcode = models.NullBooleanField(null=True, blank=True)
    # notes = models.TextField(null=True, blank=True)
    # source = models.TextField(null=False)
    nickname = models.CharField(max_length=10, null=True)
    categories = models.CharField(max_length=500, null=True, blank=True)

    # Sequence related
    sequence = models.TextField(null=False)
    # sequence_sha1 = models.BinaryField(max_length=20, null=True)
    # sequence_update = models.IntegerField(null=True, default=5)
    # seq_edit_cache = models.TextField(null=True, blank=True)
    sequence_length = models.IntegerField(null=True, default=0)  # filtering

    # Review related
    # review_result = models.FloatField(null=True, blank=True)
    review_count = models.IntegerField(null=True, blank=True)  # ordering
    review_total = models.IntegerField(null=True, blank=True)  # ordering

    ac = PackedField(null=True)
    ruler = PackedField(null=True)

    document = models.OneToOneField(
        'forum.Article',
        null=True,
        on_delete=models.SET_NULL,
        default=None
    )

    # 1 or NULL, trash field
    # flag = models.IntegerField(null=True, blank=True)

    # meaningless fields
    # temp_1 = models.IntegerField(null=True, blank=True)
    # temp_2 = models.IntegerField(null=True, blank=True)
    # temp_3 = models.IntegerField(null=True, blank=True)
    # temp4 = models.IntegerField(null=True, blank=True)

    # 0 or 1, trash field
    # rating = models.IntegerField(null=True, default=0)

    class Meta:
        db_table = 'biobricks'
        managed = False

    @property
    def users_watching(self):
        return _related_user_queryset(WatchingUser, self)

    @property
    def users_rated(self):
        return _related_user_queryset(RatedUser, self)

    @property
    def users_starred(self):
        return _related_user_queryset(StarredUser, self)

    @property
    def meta_instance(self):
        if not hasattr(self, '_meta_instance'):
            self._meta_instance = self.ensure_meta_exists(fetch=True)

        return self._meta_instance

    def ensure_meta_exists(self, fetch=False):

        meta = None

        if not self.meta_exists:
            meta = BiobrickMeta(part_name=self.part_name)
            meta.save(fill_shared_fields=True)
        elif fetch:
            meta = BiobrickMeta.objects.get(part_name=self.part_name)

        if meta is not None:
            self.group_name = meta.group_name

        return meta

    def watch(self, user):
        if WatchingUser.objects.filter(brick=self.part_name, user=user.pk).exists():
            return False

        with transaction.atomic():
            meta = self.ensure_meta_exists(fetch=True)
            WatchingUser.objects.create(brick=meta, user=user)
            meta.watches += 1
            meta.save(update_fields=['watches'])
            watching_brick_signal.send(sender=Biobrick, instance=self, user=user)

        return True

    def unwatch(self, user):

        with transaction.atomic():
            num, _ = WatchingUser.objects.filter(brick=self.part_name, user=user.pk).delete()

            if num:
                BiobrickMeta.objects.filter(part_name=self.part_name)\
                    .update(watches=models.F('watches') - 1)
                unwatching_brick_signal.send(sender=Biobrick, instance=self, user=user)
                return True
            else:
                return False

    def star(self, user):
        if StarredUser.objects.filter(brick=self.part_name, user=user.pk).exists():
            return False

        with transaction.atomic():
            meta = self.ensure_meta_exists(fetch=True)
            StarredUser.objects.create(brick=meta, user=user)
            meta.stars += 1
            meta.save()

        return True

    def unstar(self, user):

        with transaction.atomic():
            num, _ = StarredUser.objects.filter(brick=self.part_name, user=user.pk).delete()

            if num:
                BiobrickMeta.objects.filter(part_name=self.part_name)\
                    .update(stars=models.F('stars') - 1)
                return True
            else:
                return False

    def rate(self, user, score):
        if RatedUser.objects.filter(user=user.pk, brick=self.part_name).exists():
            return False

        with transaction.atomic():
            meta = self.ensure_meta_exists(fetch=True)
            meta.rate_score = (
                (meta.rate_score * meta.rates + decimal.Decimal(score)) / (meta.rates + 1)
            )
            meta.rates += 1
            RatedUser.objects.create(brick=meta, user=user, score=score)
            meta.save(update_fields=['rates', 'rate_score'])
            rating_brick_signal.send(
                sender=Biobrick,
                user_rating=user,
                instance=self,
                rating_score=score,
                curr_score=meta.rate_score
            )

        return True


class Part(models.Model):
    # The official model of biobrick from parts.igem.org
    part_id = models.AutoField(primary_key=True)
    ok = models.NullBooleanField(default=True)
    part_name = models.CharField(max_length=255, null=True, blank=True)
    short_desc = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    part_type = models.CharField(max_length=20, null=True, blank=True)
    author = models.CharField(max_length=200, null=True, blank=True)
    owning_group_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    dominant = models.NullBooleanField(default=False)
    informational = models.NullBooleanField(default=False)
    discontinued = models.IntegerField(null=True, default=0)
    part_status = models.CharField(max_length=40, null=True)
    sample_status = models.CharField(max_length=40, null=True)
    p_status_cache = models.CharField(max_length=1000, null=True)
    s_status_cache = models.CharField(max_length=1000, null=True)
    creation_date = models.DateField(null=True, blank=True)
    m_datetime = models.DateTimeField(null=True, blank=True)
    m_user_id = models.IntegerField(null=True, default=0)
    uses = models.IntegerField(null=True, default=-1)
    doc_size = models.IntegerField(null=True, default=0)
    works = models.CharField(max_length=10, null=False)
    favorite = models.IntegerField(null=True, default=0)
    specified_u_list = models.TextField(null=True, blank=True)
    deep_u_list = models.TextField(null=True, blank=True)
    deep_count = models.IntegerField(null=True, blank=True)
    ps_string = models.TextField(null=True, blank=True)
    scars = models.CharField(max_length=20, null=True, default='10')
    default_scars = models.CharField(max_length=20, null=False, default='10')
    owner_id = models.IntegerField(null=True, blank=True)
    group_u_list = models.TextField(null=True, blank=True)
    has_barcode = models.NullBooleanField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    source = models.TextField(null=False)
    nickname = models.CharField(max_length=10, null=True)
    categories = models.CharField(max_length=500, null=True, blank=True)
    sequence = models.TextField(null=False)
    sequence_sha1 = models.BinaryField(max_length=20, null=True)
    sequence_update = models.IntegerField(null=True, default=5)
    seq_edit_cache = models.TextField(null=True, blank=True)
    review_result = models.FloatField(null=True, blank=True)
    review_count = models.IntegerField(null=True, blank=True)
    review_total = models.IntegerField(null=True, blank=True)
    flag = models.IntegerField(null=True, blank=True)
    sequence_length = models.IntegerField(null=True, default=0)
    temp_1 = models.IntegerField(null=True, blank=True)
    temp_2 = models.IntegerField(null=True, blank=True)
    temp_3 = models.IntegerField(null=True, blank=True)
    temp4 = models.IntegerField(null=True, blank=True)
    rating = models.IntegerField(null=True, default=0)

    status_w = models.FloatField()
    sample_status_w = models.FloatField()
    works_w = models.FloatField()
    doc_size_w = models.FloatField()
    uses_w = models.FloatField()
    review_total_w = models.FloatField()
    review_count_w = models.FloatField()
    deep_count_w = models.FloatField()
    ac = models.TextField()
    ruler = models.TextField()

    class Meta:
        db_table = 'parts'
        managed = False
