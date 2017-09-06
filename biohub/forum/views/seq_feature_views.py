from rest_framework import viewsets, mixins, generics
from ..serializers import SeqFeatureSerializer
from ..models import SeqFeature
from biohub.utils.rest import pagination


class SeqFeatureViewSet(mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = SeqFeatureSerializer
    queryset = SeqFeature.objects.all()

    # override this function to provide "request" as "None"
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': None,
            'format': self.format_kwarg,
            'view': self
        }


class SeqFeaturesOfBricksListView(generics.ListAPIView):
    serializer_class = SeqFeatureSerializer
    pagination_class = pagination.factory('PageNumberPagination')

    def get_queryset(self):
        brick = self.kwargs['brick_id']
        return SeqFeature.objects.filter(brick=brick).order_by('id')
