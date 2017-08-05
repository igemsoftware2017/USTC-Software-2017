# -*- coding:utf-8 -*-
from rest_framework.test import APITestCase

from biohub.accounts.models import User
from biohub.abacus.models import Abacus
from biohub.abacus.responses import upload_file,get_download_file,calculate,get_status,delete_file
from biohub.abacus.aux_calculate import CALCULATE_QUEUE
from biohub.abacus.aux_responses import download_file_service
#from biohub.abacus.views import  调不出任何东西

class AbacusTestCase(APITestCase):#测试顺序：数字>大写字母>小写字母，每个函数setup都会运行一遍
    #每一对测试进行后，数据库中的数据都会失效

    def setUp(self):
        self.user=User.objects.create_user(username="use_tester",email="123456@qq.com",password="123456")
        self.other=User.objects.create_user(username="use_nontester",email="12dsg6@qq.com",password="123atsre6")
        self.client.force_login(self.user)
        self.data1 =["test","It is great!",True,False]  #block是一个一维数组,data[3]T or F有截然不同的两种结果
        self.data2 =["god!","It is unbelievable",True,False]
        #zip函数中不能多对一，不然只会显示一组数据
        self.jsn = {
            'data':[self.data1,self.data2]
        }
        self.files=[open("tests/abacus/input.pdb"),open("tests/abacus/out.pdb")]

    def test_1_upload_file(self):  #把文件内容重写了一遍，放在了str(id).pdb中
        response = upload_file(self.user, self.jsn, self.files)
        #ret_data中有两组buf，两组数据
        abacus_use = Abacus.objects.filter(user=self.user)[0]
        #数据库中信息按时间降序排列
        #尽量具有普适性
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"data": [[0, %a, true, ""], [1, %a, true, ""]]}' % (abacus_use.id-1,abacus_use.id))
        data1 = ["test","It is great!",True,True]   #要求计算
        jsn = {
            'data':[data1,self.data2]
        }
        response = upload_file(self.user, jsn, self.files)
        abacus_use_other = Abacus.objects.filter(user=self.user)[1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(abacus_use_other.id,CALCULATE_QUEUE[-1])
        #利用CALCULATE_QUEUE，把要计算的Abacus的id都放进去，CALCULATE_QUEUE是全局变量吗？多个线程？
        #功能检测完毕，成功调转，文件成功储存，返回值正确，要calculate的id正确


    def test_2_get_download_file(self):
        upload_file(self.user, self.jsn, self.files)
        abacus_use = Abacus.objects.filter(user=self.user)[0]
        id = [abacus_use.id-1,abacus_use.id]
        response = get_download_file(self.user,id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'{"data": [[0, %a, true, null, ""], [1, %a, true, null, ""]]}' % (abacus_use.id - 1, abacus_use.id))
        # 因为calculate没写好，无法自然产生download文件,所以第4个元素为null


    def test_3_get_status(self):
        upload_file(self.user, self.jsn, self.files)
        abacus_use = Abacus.objects.filter(user=self.user)[0]
        id = [abacus_use.id-1,abacus_use.id]
        response = get_status(self.user,id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'{"data": [[0, %a, true, 1, ""], [1, %a, true, 1, ""]]}' % (abacus_use.id - 1, abacus_use.id))

    def test_4_delete_file(self):
        upload_file(self.user, self.jsn, self.files)
        abacus_use = Abacus.objects.filter(user=self.user)[0]
        id = [abacus_use.id-1,abacus_use.id]
        response = delete_file(self.user,id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'{"data": [[0, -1, true, 0, ""], [1, -1, true, 0, ""]]}')




    def test_5_calculate(self):#上传之后就摁计算键，id是一个数组，应该是CALCULATE_QUEUE
        upload_file(self.user, self.jsn, self.files)
        abacus_use = Abacus.objects.filter(user=self.user)[0]
        id = [abacus_use.id-1,abacus_use.id]
        response = calculate(self.user,id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(abacus_use.id, CALCULATE_QUEUE[-1])
        self.assertEqual(response.content,
                         b'{"data": [[0, %a, true, 2, ""], [1, %a, true, 2, ""]]}' % (abacus_use.id - 1, abacus_use.id))
        #调转正确，结果正确，CALCULATE_QUEUE里的id正确

    def test_6_download_file_service(self):
        upload_file(self.user, self.jsn, self.files)
        abacus_use = Abacus.objects.filter(user=self.user)[0]
        abacus_use.shared=False
        abacus_use.save()
        response = download_file_service(self.other,abacus_use.id)
        self.assertIn(b"Access denied!",response.content)
        #未完待续，Http404()怎么在response中表述





