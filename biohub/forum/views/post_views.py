from rest_framework import viewsets, decorators
from biohub.forum.serializers import PostSerializer
from biohub.utils.rest import pagination, permissions
from biohub.forum.models import Post
from biohub.accounts.models import User


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    pagination_class = pagination.factory('PageNumberPagination')
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        query_set = Post.objects.all()
        author = self.request.query_params.get('author', None)
        if author is not None:
            query_set = Post.objects.filter(user=User.objects.get(username=author))
        return query_set

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @decorators.list_route(methods=['POST'], permission_classes=(permissions.IsAuthenticated,))
    def up_vote(self, request, *args, **kwargs):
        self.get_object().up_vote(User.objects.get(username=request.user))

    @decorators.list_route(methods=['POST'], permission_classes=(permissions.IsAuthenticated,))
    def cancel_up_vote(self, request, *args, **kwargs):
        self.get_object().cancel_up_vote(User.objects.get(username=request.user))
