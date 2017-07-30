from haystack import indexes

from .models import Biobrick
from .search_fields import MultipleCharField


class BiobrickIndex(indexes.SearchIndex, indexes.Indexable):
    text = MultipleCharField(document=True, model_attr=['short_desc', 'description'], null=True)
    short_desc = indexes.CharField(model_attr='short_desc', null=True)
    description = indexes.CharField(model_attr='description', null=True)
    part_name = indexes.CharField(model_attr='part_name', null=True)
    sequence = indexes.CharField(model_attr='sequence', null=True)

    def get_model(self):
        return Biobrick

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
