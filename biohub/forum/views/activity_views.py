from rest_framework import viewsets
from rest_framework import mixins
from biohub.forum.models import ActivityParam, Activity
from biohub.forum.serializers import ActivitySerializer
from biohub.utils.rest import pagination

class ActivityViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    pagination_class = pagination.factory('PageNumberPagination',page_size=15)