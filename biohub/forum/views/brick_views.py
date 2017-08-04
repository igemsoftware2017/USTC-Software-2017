from rest_framework import viewsets, status, decorators, mixins
from rest_framework.response import Response
from rest_framework.exceptions import APIException
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
    spider = BrickSpider()
    UPDATE_DELTA = datetime.timedelta(days=10)

    def has_brick_in_database(brick_name):
        try:
            Brick.objects.get(name=brick_name)
        except Brick.DoesNotExist:
            return False
        return True

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

    @decorators.list_route(methods=['GET'])
    def check_database(self, *args, **kwargs):
        brick_name = self.request.query_params.get('name', None)
        if brick_name is not None:
            if BrickViewSet.has_brick_in_database(brick_name):
                return Response('Database has it.', status=status.HTTP_200_OK)
            return Response('Database does not have it', status=status.HTTP_404_NOT_FOUND)
        return Response('Must specify param \'name\'.', status=status.HTTP_400_BAD_REQUEST)

    @decorators.list_route(methods=['GET'])
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
            if self.spider.fill_from_page(brick.name, brick=brick) is not True:
                return Response('Unable to update data of this brick!',
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = BrickSerializer(brick, context={
            'request': request
        })
        return Response(serializer.data)
    @decorators.list_route(methods=['GET'])
    def fetch(self,request):
        brick_name = requests.query_params.get('name',None)
        if(brick_name is None):
            return Response('Must specify brick name')
        else:
            if(has_brick_in_database(name)):
                brick = Brick.objects.get(name=brick_name)
                serializer = BrickSerializer(brick)
                return Response(serializer.data)
            else:
                # fetch brick's information and experiences
                if(self.spider.fill_from_page(brick_name=brick_name) is not True):
                    Response('Unable to fetch data of this brick!', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                brick = Brick.objects.get(name=brick_name)
                exp_spider = ExperienceSpider()
                if(exp_spider.fill_from_page(brick_name) is not True):
                    Response('Unable to fetch experiences of this brick!', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                serializer = BrickSerializer(brick)
                return Response(serializer.data)
                


    def list(self, request, *args, **kwargs):
        short = self.request.query_params.get('short', None)
        if short is not None and short.lower() == 'true':
            pagination_class = self.pagination_class
            page = self.paginate_queryset(self.queryset)
            serializer = BrickSerializer(page, fields=('id', 'name'), many=True)
            return self.get_paginated_response(serializer.data)
        return super(BrickViewSet, self).list(request=request, *args, **kwargs)
