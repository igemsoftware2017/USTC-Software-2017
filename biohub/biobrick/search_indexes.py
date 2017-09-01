from haystack import indexes

from .models import Biobrick


class BiobrickIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(model_attr='short_desc', null=True,
                             document=True, indexed=True)
    part_name = indexes.CharField(model_attr='part_name', null=True,
                                  indexed=True, boost=1.25)
    description = indexes.CharField(model_attr='description', null=True)
    sequence = indexes.CharField(model_attr='sequence', null=True)
    uses = indexes.IntegerField(model_attr='uses', null=True)

    def get_model(self):
        return Biobrick

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
