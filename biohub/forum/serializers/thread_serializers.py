from rest_framework import serializers
from biohub.utils.rest.serializers import ModelSerializer
from biohub.utils.rest.serializers import bind_model
from biohub.forum.models import Thread
from biohub.accounts.serializers import UserSerializer


@bind_model(Thread)
class ThreadSerializer(ModelSerializer):
    author = UserSerializer(fields=('id', 'username'))
    studio = serializers.PrimaryKeyRelatedField(write_only=True, required=False)
    brick = serializers.PrimaryKeyRelatedField(write_only=True, required=False)
    is_sticky = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Thread
        fields = ('id', 'title', 'content', 'is_sticky', 'brick', 'studio'
                  'update_time', 'pub_time', 'author')
        read_only_fields = ('id', 'update_time', 'pub_time', 'author')
