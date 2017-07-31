from rest_framework import viewsets, status
from rest_framework.response import Response
from biohub.utils.rest import permissions
from ..serializers import ArticleSerializer
from ..models import Article


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    permission_classes = [permissions.C(permissions.IsAuthenticatedOrReadOnly) &
                          permissions.check_owner('author', ('PATCH', 'PUT', 'DELETE'))]

    def list(self, request, *args, **kwargs):
        return Response('Unable to list articles.', status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
