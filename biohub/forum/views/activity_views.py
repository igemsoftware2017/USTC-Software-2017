from rest_framework import mixins
from rest_framework import viewsets

from biohub.forum.models import Activity
from biohub.forum.serializers import ActivitySerializer
from biohub.utils.rest import pagination


class ActivityViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin):
    queryset = Activity.objects.all().order_by('-acttime')
    serializer_class = ActivitySerializer
    pagination_class = pagination.factory('PageNumberPagination', page_size=15)
