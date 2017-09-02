from collections import OrderedDict

from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from haystack.query import SQ, SearchQuerySet, EmptySearchQuerySet

from .models import Biobrick
from .serializers import BiobrickSerializer

# Create your views here.

order_choices = ['part_name', '-uses']
list_default_order = 'part_name'


class BiobrickViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Biobrick.objects.all()
    serializer_class = BiobrickSerializer
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)

    def filter_queryset(self, queryset):
        order = self.request.query_params.get('order')
        order = order if order in order_choices else list_default_order
        return queryset.order_by(order)

    @list_route()
    def search(self, request):
        # url: biobrick/search
        # name: biobrick-search
        querydict = request.query_params
        context = OrderedDict()

        if querydict.get('q') is not None:
            q = querydict['q']

            queryset = SearchQuerySet().filter(
                SQ(text__contains=q) | SQ(part_name__contains=q))

            if (querydict.get('order') in order_choices):
                queryset = queryset.order_by(querydict['order'])

            queryset = queryset.load_all()

            suggestion = queryset.spelling_suggestion(q)
            if suggestion != q.lower():
                context['suggestion'] = suggestion

            if 'highlight' in querydict:
                queryset = queryset.highlight(
                    pre_tags=['<div class="highlight">'], post_tags=['</div>']
                )

        else:
            queryset = EmptySearchQuerySet()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)
        response.data.update(context)
        return response

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        else:
            return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
                self._paginator.page_size = 20
                self._paginator.max_page_size = 50
                self._paginator.page_size_query_param = 'pagesize'

        return self._paginator
