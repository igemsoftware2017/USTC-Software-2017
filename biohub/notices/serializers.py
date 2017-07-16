from biohub.utils.rest.serializers import ModelSerializer, bind_model

from .models import Notice


@bind_model(Notice)
class NoticeSerializer(ModelSerializer):

    class Meta:
        fields = ('id', 'has_read', 'message', 'category', 'created')
        model = Notice
