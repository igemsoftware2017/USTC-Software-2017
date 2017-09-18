from haystack import indexes

from .models import Biobrick


class BiobrickIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(
        model_attr='short_desc', null=True,
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
    creation_date = indexes.DateField(model_attr='creation_date', null=True)
    weight = indexes.FloatField(model_attr='weight', null=True)

    def get_model(self):
        return Biobrick

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
