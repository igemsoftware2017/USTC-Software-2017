from rest_framework import serializers
from biohub.utils.rest.serializers import ModelSerializer
from biohub.utils.rest.serializers import bind_model
from biohub.forum.models import Post
from biohub.accounts.serializers import UserSerializer


@bind_model(Post)
class PostSerializer(ModelSerializer):
    author = UserSerializer(fields=('id', 'username'))
    thread_id = serializers.PrimaryKeyRelatedField(write_only=True)
    up_vote_num = serializers.IntegerField(required=False, default=0)
    down_vote_num = serializers.IntegerField(required=False, default=0)

    class Meta:
        model = Post
        fields = ('id', 'thread_id', 'thread_url',
                  'content', 'up_vote_num', 'down_vote_num',
                  'update_time', 'pub_time', 'author')
        read_only_fields = ('id', 'update_time', 'pub_time', 'author', 'thread_url')
