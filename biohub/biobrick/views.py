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
        # TODO: advanced search
        querydict = request.query_params
        context = OrderedDict()

        if querydict.get('advanced') is not None:
            query1 = SQ(part_name__contains=querydict['part_name'])\
                if querydict.get('part_name') else None
            query2 = SQ(short_desc__contains=querydict['short_desc'])\
                if querydict.get('short_desc') else None

            if query1 is not None and query2 is not None:
                if querydict.get('and') is not None:
                    queryset = SearchQuerySet().filter(query1 & query2)
                else:
                    queryset = SearchQuerySet().filter(query1 | query2)
            elif query1 is None and query2 is None:
                queryset = EmptySearchQuerySet()
                context['hint'] = 'You have specified no query.'
            else:
                queryset = SearchQuerySet().filter(
                    query1 if query1 is not None else query2)

        elif querydict.get('q') is not None:
            q = querydict['q']

            queryset = SearchQuerySet().filter(
                SQ(text__contains=q) | SQ(part_name__contains=q))

            if (querydict.get('order') in order_choices):
                queryset = queryset.order_by(querydict['order'])

            suggestion = queryset.spelling_suggestion(q)
            if suggestion != q.lower():
                context['hint'] = 'You may have misspell the keyword.'
                context['suggestion'] = suggestion

        else:
            queryset = EmptySearchQuerySet()
            context['hint'] = 'You have specified no query.'

        if 'highlight' in querydict:
            queryset = queryset.highlight(
                pre_tags=['<class="highlight">'], post_tags=['</class>']
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)
        response.data.update(context)
        return response
