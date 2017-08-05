from rest_framework import viewsets, decorators, status, generics
from rest_framework.response import Response
from biohub.forum.serializers import PostSerializer
from biohub.utils.rest import pagination, permissions
from biohub.forum.models import Post
from biohub.accounts.models import User


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    pagination_class = pagination.factory('PageNumberPagination')
    permission_classes = [permissions.C(permissions.IsAuthenticatedOrReadOnly) &
                          permissions.check_owner('author', ('PATCH', 'PUT', 'DELETE'))]

    def get_queryset(self):
        author = self.request.query_params.get('author', None)
        if author is not None:
            if self.request.user.username == author:
                return Post.objects.filter(author=User.objects.get(username=author))
            else:
                return Post.objects.filter(author=User.objects.get(username=author),
                                           is_visible=True)
        return Post.objects.all().filter(is_visible=True)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @decorators.detail_route(methods=['POST'], permission_classes=(permissions.IsAuthenticated,))
    def up_vote(self, request, *args, **kwargs):
        if self.get_object().up_vote(User.objects.get(username=request.user)) is True:
            return Response('OK')
        return Response('Fail.', status=status.HTTP_400_BAD_REQUEST)

    @decorators.detail_route(methods=['POST'], permission_classes=(permissions.IsAuthenticated,))
    def cancel_up_vote(self, request, *args, **kwargs):
        if self.get_object().cancel_up_vote(User.objects.get(username=request.user)) is True:
            return Response('OK')
        return Response('Fail.', status=status.HTTP_400_BAD_REQUEST)


class PostsOfExperiencesListView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = pagination.factory('PageNumberPagination')

    def get_queryset(self):
        experience = self.kwargs['experience_id']
        author = self.request.query_params.get('author', None)
        if author is not None:
            return Post.objects.filter(experience=experience,
                                        author=User.objects.get(username=author))
        return Post.objects.filter(experience=experience)
