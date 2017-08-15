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
        if user is not None:
            query_set = Activity.objects.filter(
                user=User.objects.get(username=user))
        else:
            query_set = Activity.objects.all()
        return query_set.order_by('-acttime')
