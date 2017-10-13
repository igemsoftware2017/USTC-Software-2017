from rest_framework import serializers
from biohub.utils.rest.serializers import bind_model, ModelSerializer
from .models import File


@bind_model(File)
class FileSerializer(ModelSerializer):

    name = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = '__all__'
        extra_kwargs = {
            'file': {
                'use_url': True
            }
        }

    def get_name(self, obj):
        import re
        from functools import partial

        sub = partial(re.sub, r'\_[a-zA-Z0-9]{7}$', '')

        basename = obj.file.name
        if '.' not in basename:
            return sub(basename)
        else:
            base, dot, ext = basename.rpartition('.')
            return ''.join((sub(base), dot, ext))
