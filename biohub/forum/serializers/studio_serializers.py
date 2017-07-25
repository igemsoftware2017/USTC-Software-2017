from rest_framework import serializers
from biohub.utils.rest.serializers import ModelSerializer
from biohub.utils.rest.serializers import bind_model
from biohub.forum.models import Studio
from biohub.accounts.serializers import UserSerializer


@bind_model(Studio)
class StudioSerializer(ModelSerializer):
    users = UserSerializer(fields=('id', 'username'), many=True)
    administrator = UserSerializer(fields=('id', 'username'))

    class Meta:
        model = Studio
        fields = ('id', 'name', 'description', 'users', 'administrator')
        read_only_fields = ('id', 'users', 'administrator')


class QuitSerializer(serializers.ModelSerializer):
    # ok??
    # user = serializers.CharField(source='user.username')
    pass
