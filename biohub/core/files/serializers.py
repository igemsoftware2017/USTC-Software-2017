from biohub.utils.rest.serializers import bind_model, ModelSerializer
from .models import File


@bind_model(File)
class FileSerializer(ModelSerializer):

    class Meta:
        model = File
        fields = '__all__'
        extra_kwargs = {
            'file': {
                'use_url': True
            }
        }
