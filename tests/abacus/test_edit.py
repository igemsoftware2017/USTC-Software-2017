from rest_framework.test import APITestCase

from biohub.accounts.models import User
from biohub.abacus.models import Abacus
from biohub.abacus.responses import edit_abacus,list_abacus

class EditAbacusTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="use_testor", email="12345678@qq.com", password="12345678")
        self.other=User.objects.create_user(username="use_testor_other", email="123456ngdx78@qq.com", password="123dt45678")
        abacus=Abacus()
        abacus.tag="qwe";abacus.descriable="hdhfggvfd";abacus.shared=True;abacus.status=0;abacus.user=self.user
        abacus.save()
        abacus1 = Abacus()
        abacus1.tag = "rty";abacus1.descriable = "hdhfdsgggvfd";abacus1.shared = True;abacus1.status = 0;
        abacus1.user = self.user
        abacus1.save()
        abacus3=Abacus()
        abacus3.tag="qghwe";abacus3.descriable="hfgydhfggvfd";abacus3.shared=True;abacus3.status=0;abacus3.user=self.other
        abacus3.save()
        abacus4 = Abacus()
        abacus4.tag = "ruty";abacus4.descriable = "hdythfdsgggvfd";abacus4.shared = True;abacus4.status = 0;
        abacus4.user = self.other
        abacus4.save()

    def test_1_list_abacus(self):
        response=list_abacus(self.user)
        self.assertEqual(response.status_code,200)
        #成功，时间不好表示

    def test_2_edit_abacus(self):
        abacus=Abacus.objects.filter(tag="qwe")[0]
        data1 =[abacus.id,"qwe","hdhfggvfd",True,False]
        #json的输入[id，tag，describle，shared（boolen），calculate（boolen）]
        abacus1 = Abacus.objects.filter(tag="rty")[0]
        data2 =[abacus1.id,"rty","hdhfdsgggvfd",True,False]
        jsn = {
            'data':[data1,data2]
        }
        files=[open("tests/abacus/input.pdb"),open("tests/abacus/out.pdb")]
        response=edit_abacus(self.user,jsn,files)
        #mode=w+时，会覆盖原文件
        abacus_use = Abacus.objects.filter(user=self.user)[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'{"data": [[0, %a, true, ""], [1, %a, true, ""]]}' % (abacus_use.id - 1, abacus_use.id))




