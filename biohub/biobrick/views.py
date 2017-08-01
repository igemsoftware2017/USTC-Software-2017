from django.core.urlresolvers import reverse_lazy

from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from haystack.query import SearchQuerySet, EmptySearchQuerySet

from .models import Biobrick
from .serializers import BiobrickSerializer

# Create your views here.

order_choices = ['part_name', '-uses']
list_default_order = 'part_name'


class BiobrickViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Biobrick.objects.all()
    serializer_class = BiobrickSerializer

    def filter_queryset(self, queryset):
        order = self.request.query_params.get('order')
        order = order if order in order_choices else list_default_order
        return queryset.order_by(order)

    @list_route()
    def search(self, request):
        # url: biobrick/search
        # name: biobrick-search
        querydict = request.query_params
        queryset = None

        if querydict.get('q') is not None:
            queryset = queryset if queryset is not None else SearchQuerySet().all()
            queryset = queryset.auto_query(querydict['q'])

        if querydict.get('part_name') is not None:
            queryset = queryset if queryset is not None else SearchQuerySet().all()
            queryset = queryset.filter(part_name__contains=querydict['part_name'])

        if querydict.get('sequence') is not None:
            queryset = queryset if queryset is not None else SearchQuerySet().all()
            queryset = queryset.filter(sequence__contains=querydict['sequence'])

        if (queryset is not None) and (querydict.get('order') in order_choices):
            queryset = queryset.order_by(querydict['order'])

        if ('highlight' in querydict) and (queryset is not None):
            queryset = queryset.highlight(
                pre_tags=['<class="highlight">'], post_tags=['</class>']
            )

        queryset = queryset if queryset is not None else EmptySearchQuerySet()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super(BiobrickViewSet, self).get_serializer_context()
        if (self.request.path == reverse_lazy('api:biobrick:biobrick-search')):
            q = self.request.query_params['q']
            suggestion = EmptySearchQuerySet().spelling_suggestion(q)
            if suggestion != q:
                context['suggestion'] = suggestion
        return context
