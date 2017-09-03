from rest_framework import mixins
from rest_framework import viewsets

from biohub.accounts.models import User
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

        query_set = Activity.objects.all()
        if user is not None:
            query_set = query_set.filter(
                user=User.objects.get(username=user))
        if type is not None:
            query_set = query_set.filter(type__in=type.split(','))

        return query_set.order_by('-acttime')
