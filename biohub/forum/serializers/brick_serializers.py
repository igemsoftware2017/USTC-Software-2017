from rest_framework import serializers
from biohub.utils.rest.serializers import bind_model,\
    ModelSerializer
from ..models import Brick
from biohub.accounts.serializers import UserSerializer


@bind_model(Brick)
class BrickSerializer(ModelSerializer):
    api_url = serializers.HyperlinkedIdentityField(view_name='api:forum:brick-detail')
    document = serializers.HyperlinkedRelatedField(view_name='api:forum:article-detail', read_only=True)
    star_users = UserSerializer(fields=('id', 'username'), read_only=True, many=True)
    watch_users = UserSerializer(fields=('id', 'username'), read_only=True, many=True)
    experience_set = serializers.HyperlinkedRelatedField(read_only=True, many=True,
                                                         view_name='api:forum:experience-detail')
    seqFeatures = serializers.HyperlinkedRelatedField(read_only=True, many=True,
                                                      view_name='api:forum:seq_feature-detail')

    class Meta:
        model = Brick
        exclude = ('update_time',)
        read_only_fields = ('id', 'name', 'designer', 'group_name', 'part_type',
                            'nickname', 'part_status', 'sample_status', 'experience_status',
                            'use_num', 'twin_num', 'document',  'star_users',
                            'assembly_compatibility', 'parameters', 'categories',
                            'sequence_a', 'sequence_b', 'sub_parts', 'watch_users',)
