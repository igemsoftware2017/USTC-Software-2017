from rest_framework import mixins, permissions
from rest_framework import decorators
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

from django.contrib.auth import login as auth_login, logout as auth_logout
from django.core.files.storage import default_storage

from biohub.utils.rest import pagination, permissions as p
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

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = pagination.factory('CursorPagination', page_size=20)
    permission_classes = [
        p.C(p.IsAuthenticatedOrReadOnly) & p.check_owner()]
    filter_fields = ('username',)

    def get_object(self):
        return self.get_user_object()

    @decorators.detail_route(['GET'])
    def followers(self, request, *args, **kwargs):
        return pagination.paginate_queryset(
            self.get_object().followers.all(),
            self
        )

    @decorators.detail_route(['GET'])
    def following(self, request, *args, **kwargs):
        return pagination.paginate_queryset(
            self.get_object().following.all(),
            self)

    @decorators.detail_route(['POST'])
    def follow(self, request, *args, **kwargs):
        request.user.follow(self.get_object())

        return Response('OK')

    @decorators.detail_route(['POST'])
    def unfollow(self, request, *args, **kwargs):
        request.user.unfollow(self.get_object())

        return Response('OK')
