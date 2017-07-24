from django.db import models

# Create your models here.


class Biobrick(models.Model):
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

    class Meta:
        db_table = 'parts'


class Feature(models.Model):
    # The official model of feature from parts.igem.org
    feature_id = models.AutoField(primary_key=True)
    feature_type = models.CharField(max_length=200, null=True, blank=True)
    start_pos = models.IntegerField(null=True, blank=True)
    end_pos = models.IntegerField(null=True, blank=True)
    label = models.CharField(max_length=200, null=True, blank=True)
    part_id = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=200, null=True, blank=True)
    label2 = models.CharField(max_length=200, null=True, blank=True)
    mark = models.IntegerField(null=True, default=0)
    old = models.IntegerField(null=True, default=0)
    reverse = models.IntegerField(null=True, default=0)

    class Meta:
        db_table = 'parts_seq_features'
