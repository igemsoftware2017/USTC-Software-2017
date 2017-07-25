from biohub.utils.rest.serializers import bind_model, ModelSerializer
# from rest_framework import serializers

# Create your serializers here.
from .models import Biobrick, Feature


@bind_model(Feature)
class FeatureSerializer(ModelSerializer):

    class Meta:
        model = Feature
        exclude = ('feature_id', )
        read_only_fields = ('__all__', )


@bind_model(Biobrick)
class BiobrickSerializer(ModelSerializer):
    features = FeatureSerializer(many=True, read_only=True)

    class Meta:
        model = Biobrick
        exclude = ('part_id', )
        read_only_fields = ('__all__', )
