import logging
import datetime

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, decorators, mixins
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

from biohub.utils.rest import pagination, permissions
from biohub.accounts.mixins import UserPaginationMixin, BaseUserViewSetMixin
from biohub.forum.exceptions import SpiderError

from ..serializers import BrickSerializer
from ..models import Brick
from ..spiders import BrickSpider, ExperienceSpider

logger = logging.getLogger(__name__)


class BaseBrickViewSet(object):

    serializer_class = BrickSerializer
    pagination_class = pagination.factory('PageNumberPagination')
    queryset = Brick.objects.all().order_by('name')


class BrickViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   UserPaginationMixin,
                   BaseBrickViewSet,
                   viewsets.GenericViewSet):

    brick_spider = BrickSpider()
    experience_spider = ExperienceSpider()
    UPDATE_DELTA = datetime.timedelta(days=10)

    # lookup value can either be id or part name
    loopup_value_regex = r'\d+|(?:BBa_|pSB)[\w-]+'

    def get_lookup_options(self):
        """
        Parses kwargs and returns corresponding querying keyword arguments.
        """
        lookup = self.kwargs[self.lookup_url_kwarg or self.lookup_field]
        options = {}

        try:
            options['pk'] = int(lookup)
        except ValueError:
            options['name'] = lookup

        return options

    def get_object(self):
        """
        This function is overrided to support two-way retrieving and caching.
        """
        if hasattr(self, '_object'):
            return self._object

        queryset = self.filter_queryset(self.get_queryset())
        self._object = get_object_or_404(queryset, **self.get_lookup_options())

        return self._object

    def get_queryset(self):
        """
        This function is overrided to support fuzzy querying on `name`.
        """
        keyword = self.request.query_params.get('name', None)

        if keyword is not None:
            return Brick.objects.filter(name__icontains=keyword).order_by('name')
        else:
            return self.queryset

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        Override this function to provide "request" as None.
        """
        return {
            'request': None,
            'format': self.format_kwarg,
            'view': self
        }

    def retrieve(self, request, *args, **kwargs):
        """
        The function is overrided to support two-way retrieving:

         + when lookup via id, brick will only be searched from local database
         + when lookup via name, brick will be searched firstly in local
           database, and returned if in existence, else looked up from igem
           offical pages
        """
        lookup_options = self.get_lookup_options()

        try:
            brick = Brick.objects.get(**lookup_options)
        except Brick.DoesNotExist:

            if 'name' not in lookup_options:
                raise NotFound

            brick_name = lookup_options['name']
            should_fetch = True
            brick = None
        else:
            should_fetch = timezone.now() - brick.update_time > self.UPDATE_DELTA
            brick_name = brick.name

        if should_fetch:
            try:
                self.update_brick(brick=brick, brick_name=brick_name)
            except Exception as e:
                raise

            brick = self.get_object()

        serializer = BrickSerializer(brick, context=dict(request=None))
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        This function is overrided to support short-form retrieving.
        """
        short = self.request.query_params.get('short', '')

        if short.lower() == 'true':
            page = self.paginate_queryset(self.get_queryset())
            serializer = BrickSerializer(
                page,
                fields=('api_url', 'id', 'name'),
                many=True,
                context={'request': None}
            )
            return self.get_paginated_response(serializer.data)

        return super(BrickViewSet, self).list(request=request, *args, **kwargs)

    @staticmethod
    def update_brick(brick_name, brick):
        """
        To fetch a brick from igem offical pages.
        """
        try:
            BrickViewSet.brick_spider.fill_from_page(brick_name, brick=brick)
            BrickViewSet.experience_spider.fill_from_page(brick_name)
        except SpiderError as e:
            raise e.api_exception

    # Magical: dynamically binds functions onto the class
    for view_name, attribute in (
        ('watched_users', 'watch_users'),
        ('rated_users', 'rate_users'),
        ('starred_users', 'star_users')
    ):
        locals()[view_name] = decorators.detail_route(methods=['GET'])(
            # use closure to generate a scope
            (lambda attribute:
                # view
                lambda self, *args, **kwargs:
                    self.paginate_user_queryset(
                        getattr(self.get_object(), attribute).all()
                    )
             )(attribute)
        )

    def assert_brick_action(self, action, success='OK', fail='Fail'):
        """
        This is a helper function to reduce code duplication.

        `action` should be a callable accepting a Brick object and returning a
        bool.
        `success` and `fail` are optional response payload.
        """
        if action(self.get_object()):
            return Response(success)
        else:
            raise ValidationError(fail)

    # Extra actions

    # Magical: dynamically binds functions onto the class
    for view_name, action in (
        ('watch', lambda self, b: b.watch(self.request.user)),
        ('cancel_watch', lambda self, b: b.cancel_watch(self.request.user)),
        ('star', lambda self, b: b.star(self.request.user)),
        ('unstar', lambda self, b: b.unstar(self.request.user))
    ):
        locals()[view_name] = decorators.detail_route(
            methods=['POST'], permission_classes=(permissions.IsAuthenticated,)
        )(
            # use closure to generate a scope
            (lambda action:
                # view
                lambda self, *args, **kwargs:
                    self.assert_brick_action(
                        lambda b: action(self, b)
                    )
             )(action)
        )

    @decorators.detail_route(methods=['POST'], permission_classes=(permissions.IsAuthenticated,))
    def rate(self, request, *args, **kwargs):
        score = request.data.get('score', None)
        if score is None:
            raise ValidationError({
                'score': 'Must specify your rating score.'
            })
        return self.assert_brick_action(lambda b: b.rate(score, self.request.user))


class UserBrickViewSet(mixins.ListModelMixin, BaseBrickViewSet, BaseUserViewSetMixin):

    allowed_actions = {
        'watched_bricks': 'bricks_watched',
        'starred_bricks': 'bricks_starred',
        'rated_bricks': 'bricks_rated'
    }

    def get_queryset(self):
        try:
            return getattr(
                self.get_user_object(),
                self.allowed_actions[self.action]
            ).order_by('name')
        except KeyError:
            raise NotFound

    # Magical: Dynamically binds functions onto the class
    for view_name in allowed_actions:
        locals()[view_name] = decorators.list_route(methods=['GET'])(
            lambda self, *args, **kwargs: self.list(*args, **kwargs)
        )
