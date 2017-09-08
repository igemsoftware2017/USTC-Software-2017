from rest_framework import serializers

from biohub.utils.rest.serializers import bind_model, ModelSerializer
from biohub.accounts.serializers import UserSerializer
from ..models import Experience, Brick
from .article_serializers import ArticleSerializer
from .brick_serializers import BrickSerializer


@bind_model(Experience)
class ExperienceSerializer(ModelSerializer):
    api_url = serializers.HyperlinkedIdentityField(view_name='api:forum:experience-detail')
    content = ArticleSerializer()
    author = UserSerializer(fields=('id', 'username'), read_only=True)
    brick = BrickSerializer(read_only=True, fields=('id', 'api_url', 'name', 'part_type'))
    brick_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Brick.objects.only('id', 'name', 'part_type')
    )
    post_set = serializers.HyperlinkedRelatedField(
        read_only=True, many=True,
        view_name='api:forum:post-detail'
    )
    up_vote_users = UserSerializer(fields=('id', 'username'), read_only=True, many=True)

    class Meta:
        model = Experience
        exclude = ('update_time', )
        read_only_fields = ('author', 'author_name', 'pub_time', 'up_vote_users',
                            'content_url', 'brick_url', 'up_vote_num')

    def create(self, validated_data):
        brick = validated_data.pop('brick_id')
        content_data = validated_data.pop('content')
        content_serializer = ArticleSerializer(data=content_data)
        # In these two methods, use .create() and .update() directly without verifying.
        # Because the data validation will be accomplished by the Experience serializer.
        content = content_serializer.create(content_data)
        experience = Experience.objects.create(
            brick=brick, content=content,
            author_name=validated_data['author'].username,
            **validated_data
        )
        return experience

    def update(self, instance, validated_data):
        instance.brick = validated_data.get('brick_id', instance.brick)
        instance.author_name = validated_data['author_name']
        if 'content'in validated_data:
            content_data = validated_data.pop('content')
            content_serializer = ArticleSerializer(instance.content, data=content_data)
            content_serializer.update(instance.content, content_data)
        return super(ExperienceSerializer, self).update(instance, validated_data)
