from biohub.utils.rest.serializers import bind_model, ModelSerializer

# Create your serializers here.
from .models import Biobrick


@bind_model(Biobrick)
class BiobrickSerializer(ModelSerializer):
    # A rough one...
    # hasn't define the fields or the relationship between Biobrick and Feature
    # hasn't define the urls ( which will be placed inside the class
    class Meta:
        model = Biobrick
