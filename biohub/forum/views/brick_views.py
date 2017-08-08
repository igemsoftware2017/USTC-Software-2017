from rest_framework import viewsets, status, decorators, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from django.db.models.query import QuerySet
from biohub.utils.rest import pagination
from ..serializers import BrickSerializer
from ..models import Brick
from ..spiders import BrickSpider, ExperienceSpider
from django.utils import timezone
import datetime
import re
import requests
import logging


class BrickViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = BrickSerializer
    pagination_class = pagination.factory('PageNumberPagination')
    queryset = Brick.objects.all().order_by('name')
    brick_spider = BrickSpider()
    experience_spider = ExperienceSpider()
    UPDATE_DELTA = datetime.timedelta(days=10)

    @staticmethod
    def has_brick_in_database(brick_name):
        try:
            Brick.objects.get(name=brick_name)
        except Brick.DoesNotExist:
            return False
        return True

    @staticmethod
    def has_brick_in_igem(brick_name):
        url = 'http://parts.igem.org/cgi/xml/part.cgi?part=BBa_' + brick_name
        try:
            raw_data = requests.get(url).text
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error('Unable to visit url:' + url)
            logger.error(e)
            raise APIException
        if re.search(r'(?i)<ERROR>Part name not found.*</ERROR>', raw_data) is None \
                and re.search(r'(?i)<\s*part_list\s*/\s*>', raw_data) is None \
                and re.search(r'(?i)<\s*part_list\s*>\s*<\s*/\s*part_list\s*>', raw_data) is None:
            return True
        return False

    @staticmethod
    def update_brick(brick_name, brick):
        try:
            BrickViewSet.brick_spider.fill_from_page(brick_name, brick=brick)
            BrickViewSet.experience_spider.fill_from_page(brick_name)
        except Exception as e:
            raise

    # @decorators.list_route(methods=['GET'])
    def check_database(self, *args, **kwargs):
        brick_name = self.request.query_params.get('name', None)
        if brick_name is not None:
            if BrickViewSet.has_brick_in_database(brick_name):
                return Response('Database has it.', status=status.HTTP_200_OK)
            return Response('Database does not have it', status=status.HTTP_404_NOT_FOUND)
        return Response('Must specify param \'name\'.', status=status.HTTP_400_BAD_REQUEST)

    # @decorators.list_route(methods=['GET'])
    def check_igem(self, *args, **kwargs):
        brick_name = self.request.query_params.get('name', None)
        if brick_name is not None:
            if BrickViewSet.has_brick_in_igem(brick_name):
                return Response('iGEM has it.', status=status.HTTP_200_OK)
            return Response('iGEM does not have it', status=status.HTTP_404_NOT_FOUND)
        return Response('Must specify param \'name\'.', status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        brick = self.get_object()
        now = timezone.now()
        if now - brick.update_time > self.UPDATE_DELTA:
            try:
                self.update_brick(brick_name=brick.name, brick=brick)
                brick = self.get_object()
            except Exception as e:
                if e.args == 'The part does not exist on iGEM\'s website':
                    return Response('Unable to find this brick! ' + str(e),
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response('Unable to fetch data of this brick! ',
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = BrickSerializer(brick, context={
            'request': request
        })
        return Response(serializer.data)

    def get_queryset(self):
        ''' enable searching via URL parameter: 'name', not including 'BBa_' '''
        name_begin_with = self.request.query_params.get('name', None)
        if name_begin_with:
            return Brick.objects.filter(name__startswith=name_begin_with).order_by('name')
        else:
            # from REST framework's src code:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

    def list(self, request, *args, **kwargs):
        short = self.request.query_params.get('short', None)
        if short is not None and short.lower() == 'true':
            pagination_class = self.pagination_class
            page = self.paginate_queryset(self.get_queryset())
            serializer = BrickSerializer(page, fields=('id', 'name'), many=True)
            return self.get_paginated_response(serializer.data)
        return super(BrickViewSet, self).list(request=request, *args, **kwargs)


@api_view(['GET'])
def retrieve_brick_by_name(request, brick_name):
    # use try except directly rather than check_database() method to avoid query the database twice.
    try:
        brick = Brick.objects.get(name=brick_name)
    except Brick.DoesNotExist:
        try:
            BrickViewSet.update_brick(brick_name=brick_name, brick=None)
        except Exception as e:
            if e.args == 'The part does not exist on iGEM\'s website':
                return Response('Unable to find this brick! ' + e.args,
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response('Unable to fetch data of this brick or of the experiences.',
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        brick = Brick.objects.get(name=brick_name)
    serializer = BrickSerializer(brick, context={
        'request': request
    })
    return Response(serializer.data)
