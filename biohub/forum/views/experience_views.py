from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from biohub.forum.serializers import ExperienceSerializer
from biohub.utils.rest import pagination, permissions
from ..models import Experience
from ..spiders import ExperienceSpider
from biohub.accounts.models import User
from django.utils import timezone
import datetime


class ExperienceViewSet(viewsets.ModelViewSet):
    serializer_class = ExperienceSerializer
    pagination_class = pagination.factory('PageNumberPagination')
    permission_classes = [permissions.C(permissions.IsAuthenticatedOrReadOnly) &
                          permissions.check_owner('author', ('PATCH', 'PUT', 'DELETE'))]
    spider = ExperienceSpider()
    UPDATE_DELTA = datetime.timedelta(days=10)

    @decorators.detail_route(methods=['POST'])
    def rate(self, request, *args, **kwargs):
        score = request.data.get('score', None)
        if score is None:
            return Response('Must upload your rating score.',
                            status=status.HTTP_400_BAD_REQUEST)
        if self.get_object().rate(score, self.request.user) is True:
            return Response('OK')
        return Response('Fail.', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        author = self.request.query_params.get('author', None)
        if author is not None:
            query_set = Experience.objects.filter(author=User.objects.get(username=author))
        else:
            query_set = Experience.objects.all()
        return query_set.order_by('-pub_time', '-update_time')

    def retrieve(self, request, *args, **kwargs):
        experience = self.get_object()
        now = timezone.now()
        if now - experience.update_time > self.UPDATE_DELTA:
            if self.spider.fill_from_page(experience.brick.name, experience=experience) is not True:
                return Response('Unable to update data of this brick!',
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = ExperienceSerializer(experience, context={
            'request': request
        })
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        short = self.request.query_params.get('short', None)
        if short is not None and short.lower() == 'true':
            page = self.paginate_queryset(self.get_queryset())
            serializer = ExperienceSerializer(page, fields=('id', 'title', 'author_name'), many=True)
            return self.get_paginated_response(serializer.data)
        return super(ExperienceViewSet, self).list(request=request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
