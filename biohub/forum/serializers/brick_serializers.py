from rest_framework import serializers

from biohub.utils.rest.serializers import bind_model, ModelSerializer
from biohub.utils.rest.fields import PackedField
from biohub.accounts.serializers import UserSerializer

from .article_serializers import ArticleSerializer
from ..models import Brick


@bind_model(Brick)
class BrickSerializer(ModelSerializer):
    api_url = serializers.HyperlinkedIdentityField(
        view_name='api:forum:brick-detail')
    document = ArticleSerializer(read_only=True)
    watch_users = UserSerializer(
        fields=('id', 'username'), read_only=True, many=True)
    rate_users = UserSerializer(
        fields=('id', 'username'), read_only=True, many=True)
    experience_set = serializers.HyperlinkedRelatedField(
        read_only=True, many=True,
        view_name='api:forum:experience-detail'
    )
    seq_features = PackedField()

    class Meta:
        model = Brick
        exclude = ('update_time',)
        read_only_fields = ('id', 'name', 'designer', 'group_name', 'part_type',
                            'nickname', 'part_status', 'sample_status', 'experience_status',
                            'use_num', 'twin_num', 'document',
                            'assembly_compatibility', 'parameters', 'categories',
                            'sequence_a', 'sequence_b', 'sub_parts', 'watch_users',
                            'rate_score', 'rate_num', 'rate_users', 'star_users', 'stars')
