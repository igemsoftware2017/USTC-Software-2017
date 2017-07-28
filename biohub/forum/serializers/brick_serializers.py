from rest_framework import serializers
from biohub.utils.rest.serializers import bind_model,\
    ModelSerializer
from ..models import Brick
@bind_model(Brick)
class BrickSerializer(ModelSerializer):
    
    class Meta:
        model = Brick
        fields = '__all__'