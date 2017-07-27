from rest_framework import serializers
from biohub.utils.rest.serializers import ModelSerializer
from biohub.utils.rest.serializers import bind_model
from biohub.forum.models import Post
from biohub.accounts.serializers import UserSerializer


@bind_model(Post)
class PostSerializer(ModelSerializer):
    author = UserSerializer(fields=('id', 'username'))
    experience_id = serializers.PrimaryKeyRelatedField(write_only=True)
    up_vote_num = serializers.IntegerField(required=False, default=0)

    class Meta:
        model = Post
        fields = ('id', 'experience_id', 'experience_url',
                  'content', 'up_vote_num', 'update_time',
                  'pub_time', 'author')
        read_only_fields = ('id', 'update_time', 'pub_time', 'author', 'experience_url')


class UpVotePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id')
