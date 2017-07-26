from django.db.models import Q
from rest_framework import viewsets

from .models import Biobrick
from .serializers import BiobrickSerializer

# Create your views here.


class BiobrickViewSet(viewsets.ReadOnlyModelViewSet):
    # The viewset for bbk, to list, search and retrieve.
    queryset = Biobrick.objects.all()
    serializer_class = BiobrickSerializer

    def filter_queryset(self, queryset):
        # Return a queryset according to the request params
        querydict = self.request.query_params

        name = querydict.get('name')
        if name:
            queryset = queryset.filter(part_name__icontains=name)

        sequence = querydict.get('sequence')
        if sequence:
            queryset = queryset.filter(sequence__icontains=sequence)

        desc = querydict.get('desc', '')
        and_list = querydict.get('and', '').split(' ')
        desc += ''.join(' +' + s for s in and_list if s is not '')
        or_list = querydict.get('or', '').split(' ')
        desc += ''.join(' ' + s for s in or_list if s is not '')
        not_list = querydict.get('not', '').split(' ')
        desc += ''.join(' -' + s for s in not_list if s is not '')
        if desc is not '':
            queryset = queryset.filter(
                Q(short_desc__search=desc) | Q(description__search=desc))

        order = querydict.get('order')
        order_choices = ['part_name', '-uses']
        order = order if order in order_choices else 'part_name'
        queryset = queryset.order_by(order)

        return queryset
