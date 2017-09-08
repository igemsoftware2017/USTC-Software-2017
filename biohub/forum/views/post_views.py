from rest_framework import viewsets, generics
from biohub.forum.serializers import PostSerializer
from biohub.utils.rest import pagination, permissions
from biohub.forum.models import Post


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    pagination_class = pagination.factory('PageNumberPagination')
    permission_classes = [permissions.C(permissions.IsAuthenticatedOrReadOnly) &
                          permissions.check_owner('author', ('PATCH', 'PUT', 'DELETE'))]

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
            queryset = Post.objects.filter(author__username=author)
            if self.request.user.username != author:
                queryset = queryset.filter(is_visible=True)
            return queryset
        return Post.objects.filter(is_visible=True)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostsOfExperiencesListView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = pagination.factory('PageNumberPagination')

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
        experience = self.kwargs['experience_id']
        author = self.request.query_params.get('author', None)

        queryset = Post.objects.filter(experience=experience)
        if author is not None:
            queryset = queryset.filter(author__username=author)
        return queryset
