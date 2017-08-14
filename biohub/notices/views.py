from rest_framework import viewsets, mixins, decorators
from rest_framework.response import Response
from biohub.utils.rest import pagination, permissions as p

from .serializers import NoticeSerializer
from .models import Notice


class NoticeViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    serializer_class = NoticeSerializer
    pagination_class = pagination.factory('PageNumberPagination')
    permission_classes = [p.C(p.IsAuthenticated) &
                          p.check_owner('user', ('GET',))]
    filter_fields = ('has_read', 'category')

    def get_queryset(self):
        qs = Notice.objects.user_notices(self.request.user)

        id_list = self.request.query_params.get('ids', None)
        if id_list is not None:
            qs = qs.filter(id__in=id_list.split(','))

        return qs

    @decorators.list_route(['GET'])
    def mark_all_as_read(self, *args, **kwargs):
        self.get_queryset().mark_read()

        return Response('OK')

    @decorators.detail_route(['GET'])
    def mark_read(self, *args, **kwargs):
        self.get_object().mark_read()

        return Response('OK')

    @decorators.list_route(['GET'])
    def categories(self, *args, **kwargs):
        return Response(self.get_queryset().categories())

    @decorators.list_route(['GET'])
    def stats(self, *args, **kwargs):
        return Response(self.get_queryset().stats())
