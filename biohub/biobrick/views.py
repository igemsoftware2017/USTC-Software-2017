import logging
from functools import reduce
from operator import or_
from collections import OrderedDict

from django.shortcuts import get_object_or_404
from django.db.models import Subquery

from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets, mixins
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.decorators import detail_route, list_route
from rest_framework import permissions
from rest_framework.response import Response
from haystack.query import SQ, SearchQuerySet

from .models import Biobrick
from .serializers import BiobrickSerializer, RateSerializer
from .exceptions import SpiderError

from biohub.utils.collections import unique
from biohub.utils.rest import pagination

from biohub.accounts.mixins import UserPaginationMixin, BaseUserViewSetMixin


brick_lookup_regex = r'(?:BBa_|pSB)[\w-]+'

logger = logging.getLogger(__name__)


class BrickLookupMixin(object):

    brick_lookup_value_regex = brick_lookup_regex
    brick_lookup_url_kwarg = None

    def get_brick_lookup_options(self):
        """
        Parses kwargs and returns corresponding querying keyword arguments.
        """
        lookup = self.kwargs[
            self.brick_lookup_url_kwarg or self.lookup_url_kwarg or self.lookup_field
        ]
        return dict(part_name=lookup)

    def get_brick_object(self, queryset=Biobrick):

        if hasattr(self, '_brick_object'):
            return self._brick_object

        self._brick_object = get_object_or_404(queryset, **self.get_brick_lookup_options())
        return self._brick_object

    @classmethod
    def add_to_router(cls, router, prefix=''):
        router.register(
            r'bricks/(?P<{}>{}){}'.format(
                cls.brick_lookup_url_kwarg, cls.brick_lookup_value_regex,
                '/' + prefix if prefix else ''
            ),
            cls
        )
        return router


class BaseBrickViewSet(object):

    pagination_class = pagination.factory('PageNumberPagination')
    queryset = Biobrick.objects.all()

    @property
    def detail(self):
        if self.action == 'list':
            return False
        elif self.action == 'retrieve':
            return True
        else:
            return 'detail' in self.request.query_params

    def get_serializer_class(self):
        ret = BiobrickSerializer

        if self.action == 'list':
            return ret.list_creator()

        if not self.detail:
            ret = ret.short_creator()

        return ret


class BiobrickViewSet(
        UserPaginationMixin, BaseBrickViewSet,
        BrickLookupMixin, viewsets.ReadOnlyModelViewSet):

    renderer_classes = (JSONRenderer,)

    lookup_value_regex = brick_lookup_regex

    def get_object(self):

        if hasattr(self, '_object'):
            return self._object

        self._object = self.get_brick_object()
        return self._object

    def parse_query(self):

        queryset = SearchQuerySet()
        statements = self.request.query_params.get('q', '').split()
        keywords = []
        types = []
        names = []
        orderings = []
        highlight = False

        for statement in statements:
            if statement.startswith('o:'):
                orderings.append(statement[2:])
            if statement.startswith('n:'):
                names.append(statement[2:])
            elif statement.startswith('t:'):
                types.append(statement[2:])
            elif statement.startswith('h:'):
                highlight = True
            else:
                keywords.append(statement)

        condition = None

        for field, items in (
            ('text', keywords),
            ('part_name', names),
            ('part_type', types)
        ):
            if items:
                clause = reduce(
                    or_,
                    map(lambda kw: SQ(**{field + '__contains': kw}), items)
                )
                if condition is not None:
                    condition &= clause
                else:
                    condition = clause

        if condition is not None:
            queryset = queryset.filter(condition)

        orderings = unique(
            ['-weight', '-creation_date'] + orderings
        )
        queryset = queryset.order_by(*orderings)

        if highlight:
            queryset = queryset.highlight(
                pre_tags=['<span class="highlight">'],
                post_tags=['</span>']
            )

        return queryset

    def list(self, request, *args, **kwargs):
        context = OrderedDict()

        queryset = self.parse_query()
        queryset.load_all()

        page = self.paginate_queryset(queryset.order_by('-weight'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)
        response.data.update(context)
        return response

    def retrieve(self, request, *args, **kwargs):

        brick = self.get_object()

        if brick.should_fetch:
            try:
                brick.fetch()
            except SpiderError as e:
                logging.error(str(e))

        serializer = BiobrickSerializer(brick, context=dict(request=request))
        return Response(serializer.data)

    # User-Biobrick m2m retrieving

    for view_name, attribute in (
        ('users_watching',) * 2,
        ('users_rated',) * 2,
        ('users_starred',) * 2
    ):
        locals()[view_name] = detail_route(methods=['GET'])(
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

    for view_name, action in (
        ('watch', lambda self, b: b.watch(self.request.user)),
        ('unwatch', lambda self, b: b.unwatch(self.request.user)),
        ('star', lambda self, b: b.star(self.request.user)),
        ('unstar', lambda self, b: b.unstar(self.request.user))
    ):
        locals()[view_name] = detail_route(
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

    @detail_route(methods=['POST'], permission_classes=(permissions.IsAuthenticated,))
    def rate(self, request, *args, **kwargs):
        serializer = RateSerializer(
            data=request.data,
            context={
                'user': request.user,
                'brick': self.get_object()
            })

        if serializer.is_valid(raise_exception=True):
            result = serializer.save()
            return self.assert_brick_action(lambda b: result)


class UserBrickViewSet(mixins.ListModelMixin, BaseBrickViewSet, BaseUserViewSetMixin):

    allowed_actions = {
        'bricks_watching': 'bricks_watching',
        'bricks_starred': 'bricks_starred',
        'bricks_rated': 'bricks_rated'
    }

    def get_serializer_class(self):
        return BiobrickSerializer.list_creator()

    def get_queryset(self):
        user = self.get_user_object()

        try:
            rel_field = getattr(user, self.allowed_actions[self.action])
        except KeyError:
            raise NotFound

        return Biobrick.objects.filter(
            part_name__in=Subquery(
                rel_field.values('part_name')
            )
        ).order_by('part_name')

        # if self.detail:
        #

        # else:
        #     return rel_field.order_by('part_name')

    for view_name in allowed_actions:
        locals()[view_name] = list_route(methods=['GET'])(
            lambda self, *args, **kwargs: self.list(*args, **kwargs)
        )
