from rest_framework import serializers

from biohub.utils.rest.serializers import bind_model, ModelSerializer
from biohub.accounts.serializers import UserSerializer
from biohub.biobrick.models import BiobrickMeta
from ..models import Experience
from .article_serializers import ArticleSerializer
from biohub.biobrick.serializers import BiobrickSerializer


@bind_model(Experience)
class ExperienceSerializer(ModelSerializer):
    api_url = serializers.HyperlinkedIdentityField(view_name='api:forum:experience-detail')
    content = ArticleSerializer()
    author = UserSerializer(fields=('id', 'username', 'avatar_url'), read_only=True)
    brick = BiobrickSerializer.short_creator()(read_only=True)
    brick_name = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=BiobrickMeta.objects.only('part_name')
    )
    voted = serializers.BooleanField(read_only=True, required=False)
    posts_num = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Experience
        exclude = ('voted_users',)
        read_only_fields = ('author', 'author_name', 'pub_time',
                            'content_url', 'brick_url', 'votes')

    def create(self, validated_data):
        brick = validated_data.pop('brick_name')
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
        instance.brick = validated_data.get('brick_name', instance.brick)
        instance.author_name = validated_data['author_name']
        if 'content'in validated_data:
            content_data = validated_data.pop('content')
            content_serializer = ArticleSerializer(instance.content, data=content_data)
            content_serializer.update(instance.content, content_data)
        return super(ExperienceSerializer, self).update(instance, validated_data)
