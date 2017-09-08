from rest_framework import serializers

from biohub.utils.rest.serializers import bind_model, ModelSerializer
from ..models import SeqFeature


@bind_model(SeqFeature)
class SeqFeatureSerializer(ModelSerializer):
    brick = serializers.HyperlinkedRelatedField(view_name='api:forum:brick-detail', read_only=True)

    class Meta:
        model = SeqFeature
        exclude = ('update_time',)
        read_only_fields = ('feature_type', 'start_loc', 'end_loc', 'name',
                            'reserve', 'brick')
