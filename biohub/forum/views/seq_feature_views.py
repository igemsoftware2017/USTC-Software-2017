from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from ..serializers import SeqFeatureSerializer
from ..models import SeqFeature
from ..spiders import SeqFeatureSpider
from django.utils import timezone
import datetime


class SeqFeatureViewSet(mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = SeqFeatureSerializer
    queryset = SeqFeature.objects.all()
    spider = SeqFeatureSpider()
    UPDATE_DELTA = datetime.timedelta(days=10)

    def retrieve(self, request, *args, **kwargs):
        seq_feature = self.get_object()
        now = timezone.now()
        if now - seq_feature.update_time > self.UPDATE_DELTA:
            if self.spider.fill_from_page(seq_feature.name, seq_feature=seq_feature) is not True:
                return Response('Unable to update data of this seq_feature!',
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = SeqFeatureSerializer(seq_feature, context={
            'request': request
        })
        return Response(serializer.data)
