from haystack import indexes

from .models import Biobrick


class BiobrickIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(
        model_attr='index_description', null=True,
        document=True, indexed=True
    )
    part_name = indexes.CharField(
        model_attr='part_name', null=True,
        indexed=True, boost=1.25
    )
    part_type = indexes.CharField(
        model_attr='part_type', null=True,
        indexed=True, boost=1.25
    )
    author = indexes.CharField(
        model_attr='author', null=True,
        indexed=True, boost=1.25
    )
    creation_date = indexes.DateField(model_attr='creation_date', null=True)
    weight = indexes.FloatField(model_attr='weight', null=True)
    stars = indexes.IntegerField(model_attr='stars', null=True)
    watches = indexes.IntegerField(model_attr='watches', null=True)
    rate_score = indexes.IntegerField(model_attr='rate_score', null=True)
    uses = indexes.IntegerField(model_attr='uses')

    def get_model(self):
        return Biobrick

    def get_updated_field(self):
        return 'weight_updated_time'

    def index_queryset(self, using=None):
        return self.get_model().objects.only('short_desc', 'part_name', 'part_type', 'creation_date', 'weight', 'author', 'uses', 'stars', 'watches', 'rate_score')

    def __str__(self):
        return '<Biobrick Index for ElasticSearch>'
