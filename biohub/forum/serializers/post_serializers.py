from rest_framework import serializers
from biohub.utils.rest.serializers import ModelSerializer
from biohub.utils.rest.serializers import bind_model
from biohub.forum.models import Post, Experience
from biohub.accounts.serializers import UserSerializer

from .experience_serializers import ExperienceSerializer


@bind_model(Post)
class PostSerializer(ModelSerializer):
    author = UserSerializer(fields=('id', 'username'), read_only=True)
    experience_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Experience.objects.all()
    )
    experience = ExperienceSerializer(
        read_only=True,
    )

    class Meta:
        model = Post
        fields = ('id', 'experience_id', 'experience',
                  'content', 'update_time',
                  'pub_time', 'author')
        read_only_fields = ('id', 'update_time', 'pub_time')

    def create(self, validated_data):
        experience = validated_data.pop('experience_id')
        post = Post.objects.create(experience=experience, **validated_data)
        return post

    def update(self, instance, validated_data):
        if 'experience_id' in validated_data:
            validated_data.pop('experience_id')
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance
