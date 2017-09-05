from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.exceptions import NotFound

from .serializers import UserSerializer
from .models import User


class UserPaginationMixin(object):

    def paginate_user_queryset(self, queryset):
        page = self.paginate_queryset(queryset.order_by('id'))
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(page, many=True)
        return Response(serializer.data)


re_user_lookup_value = r'\d+|me|n:[\da-zA-Z_]{4,15}'


class BaseUserViewSetMixin(viewsets.GenericViewSet):

    user_lookup_value_regex = re_user_lookup_value

    def get_user_object(self):
        lookup = self.kwargs['user_pk']

        if lookup == 'me':

            if not self.request.user.is_authenticated():
                raise NotFound

            return self.request.user
        elif lookup.startswith('n:'):

            return get_object_or_404(User, username=lookup[2:])

        return super(BaseUserViewSetMixin, self).get_object()

    @classmethod
    def add_to_router(cls, router):
        router.register(r'users/(?P<user_pk>%s)' % cls.user_lookup_value_regex, cls)
        return router
