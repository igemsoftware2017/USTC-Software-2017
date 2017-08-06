from django.test import TestCase
from rest_framework.test import APITestCase,APIRequestFactory
import json

from biohub.accounts.models import User


class URLTestCase(APITestCase):

    def setUp(self):
        self.user=User.objects.create_user(username="use_tester",email="123456@qq.com",password="123456")
        self.client.force_login(self.user)

    def test_1_upload(self):
        #req=json.dumps(req)
        #data = {'tag':"tag",'describle':'It is great!','shared':False,'calculate':False,'files':open("tests/abacus/input.pdb")}
        dat=["tag",'It is great!',False,False]
        data = {'data':[],'files': open("tests/abacus/input.pdb")}
        data['data']=dat
        #对data的value加一个“”嘞,×，不对，这样就是一个字符串了
        factory = APIRequestFactory()
        request = factory.post('/api/abacus/upload/',data)
        #二维数组模拟不了。。。
        #request.body是无用的
#        request.POST['data']=[["tag",'It is great!',False,False]]
        print("**************************************************")
        #print(json.load(request.POST))
        #返回一个字典，这个字典是什么格式的  ，dict/querydict???
        #这样真可行吗？我觉得不好，可以把request中的数据提取出来，显式转化为dict格式
        #=====================>参考前人文献嘛
        print(request.POST['data'])
        print("**************************************************")
        print(request.FILES.getlist('files'))
        print("**************************************************")
        print(request.POST['data'][0])
        print("**************************************************")
        print(request.POST['data'][0][0])
        print("**************************************************")
#        response=self.client.post('/api/abacus/upload/',data)
#        self.assertEqual(response.status_code,200)


''' #可以转入，但abacus.html没写好，会报错
    def test_4_index(self):
        response=self.client.get('/api/abacus/index/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,"index.html")
'''