from rest_framework import viewsets

from .models import Biobrick
from .serializers import BiobrickSerializer

# Create your views here.


class BiobrickViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Biobrick.objects.all().order_by('part_name')
    # will be replaced by a get queryset function to search
    serializer_class = BiobrickSerializer
