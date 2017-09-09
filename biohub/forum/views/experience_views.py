import datetime
import logging

from django.utils import timezone
from rest_framework import viewsets, decorators, mixins
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound

from biohub.utils.rest import pagination, permissions
from biohub.accounts.mixins import UserPaginationMixin, BaseUserViewSetMixin
from biohub.forum.serializers import ExperienceSerializer
from biohub.forum.exceptions import SpiderError

from ..models import Experience
from ..spiders import ExperienceSpider
from .brick_views import BrickLookupMixin

logger = logging.getLogger('biohub.forum.views.experience_views')


class BaseExperienceViewSet(object):

    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    pagination_class = pagination.factory('PageNumberPagination')
    permission_classes = [permissions.C(permissions.IsAuthenticatedOrReadOnly) &
                          permissions.check_owner('author', ('PATCH', 'PUT', 'DELETE'))]


class ExperienceViewSet(
        BrickLookupMixin,
        UserPaginationMixin,
        BaseExperienceViewSet,
        viewsets.ModelViewSet):

    spider = ExperienceSpider()
    UPDATE_DELTA = datetime.timedelta(seconds=10)

    brick_lookup_url_kwarg = 'brick_pk'

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
                author__username=author
            )
        else:
            queryset = Experience.objects.all()
        if self.brick_lookup_url_kwarg in self.kwargs:
            options = self.get_brick_lookup_options()
            queryset = queryset.filter(
                **{
                    'brick__' + field: value
                    for field, value in options.items()
                }
            )

        return queryset.order_by('-pub_time', '-update_time')

    @decorators.detail_route(methods=['GET'])
    def voted_users(self, request, *args, **kwargs):
        return self.paginate_user_queryset(self.get_object().up_vote_users.all())

    @decorators.detail_route(methods=['POST'], permission_classes=(permissions.IsAuthenticated,))
    def up_vote(self, request, *args, **kwargs):
        if self.get_object().up_vote(request.user):
            return Response('OK')
        raise ValidationError('Fail')

    @decorators.detail_route(methods=['POST'], permission_classes=(permissions.IsAuthenticated,))
    def cancel_up_vote(self, request, *args, **kwargs):
        if self.get_object().cancel_up_vote(request.user):
            return Response('OK')
        raise ValidationError('Fail')

    def retrieve(self, request, *args, **kwargs):
        experience = self.get_object()
        # experience.author is None means it is from iGEM website,
        # rather than uploaded by a user
        if experience.author is None:
            now = timezone.now()
            if now - experience.update_time > self.UPDATE_DELTA:
                try:
                    self.spider.fill_from_page(experience.brick.name)
                except SpiderError as e:
                    logger.warn(str(e))
                else:
                    experience.refresh_from_db()
        serializer = ExperienceSerializer(
            experience,
            context={'request': None}
        )
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        # ?short=true will return only fields of (id, title, author_name)
        short = self.request.query_params.get('short', '')
        if short.lower() == 'true':
            page = self.paginate_queryset(self.get_queryset())
            serializer = ExperienceSerializer(
                page,
                fields=('api_url', 'id', 'title', 'author_name', 'author', 'brick'),
                many=True, context={'request': None}
            )
            return self.get_paginated_response(serializer.data)
        return super(ExperienceViewSet, self).list(request=request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author_name=self.request.user.username)


class UserExperienceViewSet(mixins.ListModelMixin, BaseExperienceViewSet, BaseUserViewSetMixin):

    allowed_actions = {
        'voted_experiences': 'experiences_voted'
    }

    def get_queryset(self):
        try:
            return getattr(
                self.get_user_object(),
                self.allowed_actions[self.action]
            ).order_by('-pub_time', '-update_time')
        except KeyError:
            raise NotFound

    # Magical: Dynamically binds functions onto the class
    for view_name in allowed_actions:
        locals()[view_name] = decorators.list_route(methods=['GET'])(
            lambda self, *args, **kwargs: self.list(*args, **kwargs)
        )
