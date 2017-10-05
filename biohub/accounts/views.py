from rest_framework import mixins, permissions
from rest_framework import decorators
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

from django.contrib.auth import login as auth_login, logout as auth_logout
from django.core.files.storage import default_storage
from django.db import models

from biohub.utils.rest import pagination, permissions as p
from biohub.forum.models import Experience
from biohub.biobrick.models import StarredUser
from biohub.core.files.utils import store_file

from .serializers import UserSerializer, RegisterSerializer, LoginSerializer,\
    ChangePasswordSerializer, PasswordResetRequestSerializer, PasswordResetPerformSerializer
from .models import User
from .mixins import BaseUserViewSetMixin, re_user_lookup_value


def make_view(serializer_cls):

    @decorators.api_view(['POST'])
    def handler(request):
        if request.user.is_authenticated():
            raise NotFound

        serializer = serializer_cls(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            auth_login(request, user)
            return Response(UserSerializer(user).data)

    return handler


register = make_view(RegisterSerializer)
login = make_view(LoginSerializer)


@decorators.api_view(['GET'])
@decorators.permission_classes([permissions.IsAuthenticated])
def logout(request):
    auth_logout(request)

    return Response('OK')


@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.IsAuthenticated])
def change_password(request):

    serializer = ChangePasswordSerializer(
        data=request.data, context=dict(request=request))

    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response('OK')


@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.IsAuthenticated])
def upload_avatar(request):

    if 'file' not in request.FILES:
        raise ValidationError('Field `file` not found.')

    filename, _ = store_file(request.FILES['file'])
    url = default_storage.url(filename)

    request.user.update_avatar(url)

    return Response(url)


class PasswordResetView(APIView):

    def get(self, request, *args, **kwargs):

        serializer = PasswordResetRequestSerializer(data=request.GET)

        if serializer.is_valid(raise_exception=True):
            return Response(serializer.save())

    def post(self, request, *args, **kwargs):

        serializer = PasswordResetPerformSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            return Response(serializer.save())


class UserViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.UpdateModelMixin,
        BaseUserViewSetMixin):

    lookup_value_regex = re_user_lookup_value
    lookup_url_kwarg = 'user_pk'

    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    pagination_class = pagination.factory('PageNumberPagination', page_size=20)
    permission_classes = [
        p.C(p.IsAuthenticatedOrReadOnly) & p.check_owner()]
    filter_fields = ('username',)

    def get_user_queryset(self):

        qs = super(UserViewSet, self).get_user_queryset()

        if self.action == 'retrieve':

            if self.request.user.is_authenticated():
                qs = qs.annotate(
                    followed=models.ExpressionWrapper(
                        models.Count(
                            models.Subquery(
                                User.following.through.objects.filter(
                                    to_user_id=self.request.user.id,
                                    from_user_id=models.OuterRef('id')
                                ).values('id')
                            )
                        ),
                        output_field=models.BooleanField()
                    )
                )

        return qs

    def get_object(self):
        obj = self.get_user_object()
        self.check_object_permissions(self.request, obj)
        return obj

    @decorators.detail_route(['POST'])
    def follow(self, request, *args, **kwargs):
        request.user.follow(self.get_object())

        return Response('OK')

    @decorators.detail_route(['POST'])
    def unfollow(self, request, *args, **kwargs):
        request.user.unfollow(self.get_object())

        return Response('OK')

    @decorators.detail_route(['GET'])
    def stat(self, request, *args, **kwargs):

        user = self.get_object()

        result = {
            'follower_count': user.followers.count(),
            'following_count': User.followers.through.objects.filter(to_user_id=user.id).count(),
            'star_count': StarredUser.objects.filter(user=user).count(),
            'experience_count': Experience.objects.filter(author=user).count()
        }

        return Response(result)


class UserRelationViewSet(mixins.ListModelMixin, BaseUserViewSetMixin):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = pagination.factory('PageNumberPagination', page_size=20)

    allowed_actions = {
        'followers': 'followers',
        'following': 'following'
    }

    def get_queryset(self):
        user = self.get_user_object()

        try:
            rel_field = getattr(user, self.allowed_actions[self.action])
        except KeyError:
            raise NotFound

        if self.request.user.is_authenticated():
            rel_field = rel_field.annotate(
                followed=models.ExpressionWrapper(
                    models.Count(
                        models.Subquery(
                            User.following.through.objects.filter(
                                to_user_id=self.request.user.id,
                                from_user_id=models.OuterRef('id')
                            ).values('id')
                        )
                    ),
                    output_field=models.BooleanField()
                )
            )

        return rel_field.order_by('id')

    for view_name in allowed_actions:
        locals()[view_name] = decorators.list_route(methods=['GET'])(
            lambda self, *args, **kwargs: self.list(*args, **kwargs)
        )
