from rest_framework import serializers
from biohub.utils.rest.serializers import bind_model,\
    ModelSerializer
from ..models import Experience, Brick, Article
from biohub.accounts.serializers import UserSerializer
from ..serializers import ArticleSerializer


@bind_model(Experience)
class ExperienceSerializer(ModelSerializer):
    api_url = serializers.HyperlinkedIdentityField(view_name='api:forum:experience-detail')
    content = serializers.HyperlinkedRelatedField(view_name='api:forum:article-detail',
                                                  read_only=True)
    author = UserSerializer(fields=('id', 'username'), read_only=True)
    content_data = ArticleSerializer(write_only=True)
    brick = serializers.HyperlinkedRelatedField(view_name='api:forum:brick-detail',
                                                read_only=True)
    brick_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Brick.objects.all())
    # posts = serializers.HyperlinkedRelatedField

    class Meta:
        model = Experience
        exclude = ('update_time',)
        read_only_fields = ('author', 'author_name', 'pub_time',
                            'content_url', 'brick_url')

    def create(self, validated_data):
        brick = validated_data.pop('brick_id')
        content_data = validated_data.pop('content_data')
        content_serializer = ArticleSerializer(data=content_data)
        # In these two method, use .create() and .update() directly without verifying.
        # Because the data validation will be accomplished by the Experience serializer.
        content = content_serializer.create(content_data)
        experience = Experience.objects.create(brick=brick, content=content,
                                               author_name=validated_data['author'].username,
                                               **validated_data)
        return experience

    def update(self, instance, validated_data):
        instance.brick = validated_data.get('brick_id', instance.brick)
        instance.author_name = validated_data['author_name']
        if 'content_data'in validated_data:
            content_data = validated_data.pop('content_data')
            content_serializer = ArticleSerializer(instance.content, data=content_data)
            content_serializer.update(instance.content, content_data)
        return super(ExperienceSerializer, self).update(instance, validated_data)
