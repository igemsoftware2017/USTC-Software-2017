from biohub.utils.rest.serializers import bind_model, ModelSerializer
from biohub.utils.rest.fields import PackedField

from ..models import Activity


@bind_model(Activity)
class ActivitySerializer(ModelSerializer):

    params = PackedField()

    class Meta:
        model = Activity
        exclude = ('user', 'id')
        read_only_fields = ('type', 'params', 'acttime',)

    def to_representation(self, obj):

        result = super(ActivitySerializer, self).to_representation(obj)
        result['params'].update({
            'user': obj.user.username,
            'type': obj.type
        })

        return result
