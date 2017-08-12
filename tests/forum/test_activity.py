from django.test import TestCase
from biohub.forum.models import Activity, ActivityParam
from biohub.forum.serializers import ActivityParamSerializer
from biohub.accounts.models import User

class ActivityParamTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='abc')
        self.user.set_password('123456000+')
        self.user.save()
        
    def test_param_serialization(self):
        self.param = ActivityParam.objects.create(type='Experience',user=self.user,partName='B0015',expLink='/api/forum/experiences/15',intro='')
        
        param_serializer = ActivityParamSerializer(self.param)
        data = param_serializer.data
        # self.assertEqual(len(data),4)
        param2 = ActivityParam.objects.create(type='Comment',user=self.user,partName='B0015',expLink='/api/forum/experiences/15',intro='')
        param3 = ActivityParam.objects.create(type='Star',user=self.user,partName='B0015',expLink='/api/forum/experiences/15',intro='')
        param4 = ActivityParam.objects.create(type='Rating',user=self.user,partName='B0015',expLink='/api/foorum/experiences/15',score=3.7)
        set_serializer = ActivityParamSerializer(ActivityParam.objects.all(),many=True)
        data_set = set_serializer.data
        pass