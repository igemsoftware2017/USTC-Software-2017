from rest_framework import mixins
from rest_framework import viewsets

from biohub.forum.models import Activity
from biohub.forum.serializers import ActivitySerializer
from biohub.utils.rest import pagination


class ActivityViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin):
    serializer_class = ActivitySerializer
    pagination_class = pagination.factory('PageNumberPagination')

    def get_queryset(self):
        user = self.request.query_params.get('user', None)
        type = self.request.query_params.get('type', None)

        queryset = Activity.objects.all()
        if user is not None:
            queryset = queryset.filter(user__username=user)
        if type is not None:
            queryset = queryset.filter(type__in=type.split(','))

        return queryset.order_by('-acttime')
