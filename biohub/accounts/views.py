from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from django.contrib.auth import login as auth_login, logout as auth_logout

from biohub.utils.rest import pagination, permissions as p

from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from .models import User


def make_view(serializer_cls):

    @api_view(['POST'])
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


@api_view(['GET'])
def logout(request):
    if not request.user.is_authenticated():
        raise NotFound

    auth_logout(request)

    return Response('OK')


class UserViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = pagination.factory('CursorPagination', page_size=20)
    permission_classes = [
        p.C(p.IsAuthenticatedOrReadOnly) & p.check_owner()]
