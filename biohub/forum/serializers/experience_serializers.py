from rest_framework import serializers

from biohub.utils.rest.serializers import ModelSerializer
from biohub.accounts.serializers import UserSerializer
from biohub.biobrick.models import BiobrickMeta
from ..models import Experience
from .article_serializers import ArticleSerializer


class ExperienceSerializer(ModelSerializer):

    api_url = serializers.HyperlinkedIdentityField(view_name='api:forum:experience-detail')
    author = UserSerializer(fields=('id', 'username', 'avatar_url'), read_only=True)
    brick_name = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=BiobrickMeta.objects.only('part_name')
    )
    voted = serializers.BooleanField(read_only=True, required=False)
    posts_num = serializers.IntegerField(read_only=True, required=False)
    content_input = ArticleSerializer(write_only=True)

    title = serializers.CharField(required=True)

    class Meta:
        model = Experience
        exclude = ('voted_users',)
        read_only_fields = ('author', 'author_name', 'pub_time',
                            'content_url', 'brick_url', 'votes')

    def create(self, validated_data):
        brick = validated_data.pop('brick_name')
        content_serializer = validated_data.pop('content_input')
        content = content_serializer.save()
        experience = Experience.objects.create(
            brick=brick, content=content,
            author_name=validated_data['author'].username,
            **validated_data
        )
        return experience

    def validate_content_input(self, value):

        if self.instance is None:
            serializer = ArticleSerializer(data=value)
        else:
            serializer = ArticleSerializer(self.instance.content, data=value, partial=True)
        serializer.is_valid(raise_exception=True)

        return serializer

    def update(self, instance, validated_data):
        instance.brick = validated_data.get('brick_name', instance.brick)
        instance.author_name = validated_data['author_name']
        if 'content_input' in validated_data:
            validated_data.pop('content_input').save()
        return super(ExperienceSerializer, self).update(instance, validated_data)


class ShortExperienceSerializer(ExperienceSerializer):

    content = ArticleSerializer(fields=('digest', 'files'), read_only=True)


class DetailExperienceSerializer(ExperienceSerializer):

    content = ArticleSerializer(fields=('text', 'files'), read_only=True)
