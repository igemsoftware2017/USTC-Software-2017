from rest_framework import viewsets, status
from rest_framework.response import Response
from ..serializers import ArticleSerializer
from ..models import Article


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ArticleSerializer
    queryset = Article.objects.all()

    def list(self, request, *args, **kwargs):
        return Response('Unable to list articles.', status=status.HTTP_404_NOT_FOUND)
