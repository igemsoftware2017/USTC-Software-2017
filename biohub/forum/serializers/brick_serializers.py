from rest_framework import serializers
from biohub.utils.rest.serializers import bind_model,\
    ModelSerializer
from ..models import Brick, Experience, SeqFeature

class SeqFeatureSerializer(ModelSerializer):

    class Meta:
        model = SeqFeature
        exclude = ('brick')

class ExperienceEntrySerializer(ModelSerializer):
    """
    Shows entrance information (title and id)
    used to generate titles and URLs in frontend
    """
    class Meta:
        model = Experience
        fields = ('id','title')


@bind_model(Brick)
class BrickSerializer(ModelSerializer):
    
    experience_set = ExperienceEntrySerializer(many=True,read_only=True)
    seqFeatures = SeqFeatureSerializer(many=True,read_only=True)
    class Meta:
        model = Brick
        fields = '__all__'
