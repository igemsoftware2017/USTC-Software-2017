from rest_framework import viewsets, exceptions
from biohub.forum.serializers.post_serializers import PostSerializer
from biohub.utils.rest import pagination, permissions
from biohub.forum.models import Post


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    pagination_class = pagination.factory('PageNumberPagination', page_size=10)
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
        else:
            queryset = Post.objects.filter(is_visible=True)

        if 'experience_id' in self.kwargs:
            queryset = queryset.filter(experience__id=self.kwargs['experience_id'])

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        from biohub.core.conf import settings as biohub_settings
        from datetime import timedelta
        from django.utils.timezone import now

        user = self.request.user
        if Post.objects.filter(
            author=user,
            pub_time__gte=now() - timedelta(seconds=biohub_settings.THROTTLE['post'])
        ).exists():
            raise exceptions.Throttled()

        return super(PostViewSet, self).create(request, *args, **kwargs)
