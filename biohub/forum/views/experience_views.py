from rest_framework import viewsets, status, decorators, generics
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

    def get_queryset(self):
        author = self.request.query_params.get('author', None)
        if author is not None:
            queryset = Experience.objects.filter(
                author=User.objects.get(username=author))
        else:
            queryset = Experience.objects.all()
        return queryset.order_by('-pub_time', '-update_time')

    @decorators.detail_route(methods=['POST'], permission_classes=(permissions.IsAuthenticated,))
    def up_vote(self, request, *args, **kwargs):
        if self.get_object().up_vote(request.user):
            return Response('OK')
        return Response('Fail.', status=status.HTTP_400_BAD_REQUEST)

    @decorators.detail_route(methods=['POST'], permission_classes=(permissions.IsAuthenticated,))
    def cancel_up_vote(self, request, *args, **kwargs):
        if self.get_object().cancel_up_vote(request.user):
            return Response('OK')
        return Response('Fail.', status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        experience = self.get_object()
        # experience.author is None means it is from iGEM website,
        # rather than uploaded by a user
        if experience.author is None:
            now = timezone.now()
            if now - experience.update_time > self.UPDATE_DELTA:
                try:
                    self.spider.fill_from_page(experience.brick.name)
                    experience = self.get_object()
                except Exception as e:
                    return Response('Unable to update data of this experience!',
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = ExperienceSerializer(experience, context={
            'request': None
        })
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        # ?short=true will return only fields of (id, title, author_name)
        short = self.request.query_params.get('short', None)
        if short is not None and short.lower() == 'true':
            page = self.paginate_queryset(self.get_queryset())
            serializer = ExperienceSerializer(page, fields=(
                'api_url', 'id', 'title', 'author_name', 'author', 'brick'),
                many=True, context={
                'request': None
            })
            return self.get_paginated_response(serializer.data)
        return super(ExperienceViewSet, self).list(request=request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author_name=self.request.user.username)


class ExperiencesOfBricksListView(generics.ListAPIView):
    serializer_class = ExperienceSerializer
    pagination_class = pagination.factory('PageNumberPagination')

    def get_queryset(self):
        brick = self.kwargs['brick_id']
        author = self.request.query_params.get('author', None)
        if author is not None:
            return Experience.objects.filter(
                brick=brick,
                author=User.objects.only('pk').get(username=author)
            )
        return Experience.objects.filter(brick=brick)

    def get(self, request, *args, **kwargs):
        # ?short=true will return only fields of (id, title, author_name)
        short = self.request.query_params.get('short', None)
        if short is not None and short.lower() == 'true':
            page = self.paginate_queryset(self.get_queryset())
            serializer = ExperienceSerializer(page, fields=(
                'api_url', 'id', 'title', 'author_name', 'author'), many=True, context={
                'request': None
            })
            return self.get_paginated_response(serializer.data)
        return super(ExperiencesOfBricksListView, self).get(request=request, *args, **kwargs)
