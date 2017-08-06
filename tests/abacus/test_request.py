# from django.test import TestCase, RequestFactory
# import json
#
# from biohub.abacus.views import AbacusView
# from biohub.accounts.models import User
# from django.test import client
# from rest_framework.test import APITestCase
# from django.http import Http404
#
# from biohub.accounts.models import User
# from biohub.abacus.models import Abacus
# from biohub.abacus import responses
#
#
# class SimpleTest(TestCase):
#     def setUp(self):
#         # Every test needs access to the request factory.
#         self.factory = RequestFactory()
#         self.user = User.objects.create_user(
#             username='jacob', password='top_secret')
#
#         self.john = User.objects.create_user(username='john', password='password')
#         self.lili = User.objects.create_user(username='lili', password='password')

    # def test_download(self):
    #     data = ['tag', 'describle', True, True]
    #     file = open("biohub/abacus/storage/download/download.pdb")
    #     jsn = {'data': [data, data, data, ], }
    #     files = [file, file, file, ]
    #
    #     c = client.Client()
    #     # {'name': 'files', 'attachment': files}
    #     response = c.get('/api/abacus/download/', {'id' : 1})
    #     print(response.status_code, response.content)

    # error!!!!
    # def test_upload(self):
    #     data = ['tag', 'describle', True, True]
    #     file = open("biohub/abacus/storage/download/download.pdb")
    #     jsn = {'data': [data, data, data, ], }
    #     files = [file, file, file, ]
    #
    #     c = client.Client()
    #     c.put('files', files, content_type='APPLICATION/OCTET-STREAM')
    #
    #     # {'name': 'files', 'attachment': files}
    #     response = c.post('/api/abacus/upload/', jsn)
    #     # print(response.status_code, response.content)
    #     print(response.status_code)

    # Error!!!
    # def test_edit(self):
    #
    #     data = ['tag', 'describle', True, True]
    #     file = open("biohub/abacus/storage/download/download.pdb")
    #
    #     jsn = {'data': [data, data, data, ], }
    #     files = [file, file, file, ]
    #
    #     response = responses.upload_file(self.john, jsn, files)
    #     print("\nupload -> ", response.content)
    #
    #     # test normal
    #     jsn = {'method' : 'edit', 'data' : [[p.id, 'ntag', 'ndescriable', True, True] for p in Abacus.objects.filter(user=self.john) ]}
    #     # response = responses.edit_abacus(self.john, jsn, files)
    #     # print("\nedit -> ", response.content)
    #     # response = responses.list_abacus(self.john)
    #     # print("\nlist -> ", response.content)
    #
    #     c = client.Client()
    #     response = c.post('/api/abacus/action/', jsn)
    #     print(response.status_code, response.content)


        # test normal without files
        # jsn = {'data' : [[p.id, 'ntag', 'ndescriable', True, True] for p in Abacus.objects.filter(user=self.john) ]}
        # response = response_tool.edit_abacus(self.john, jsn, [None for p in Abacus.objects.filter(user=self.john)])
        # print("\nedit -> ", response.content)
        # response = response_tool.list_abacus(self.john)
        # print("\nlist -> ", response.content)

        # test access denied
        # jsn = {'data' : [[p.id, 'ntag', 'ndescriable', True, True] for p in Abacus.objects.filter(user=self.john) ]}
        # response = response_tool.edit_abacus(self.lili, jsn, files)
        # print("\nedit -> ", response.content)
        # response = response_tool.list_abacus(self.john)
        # print("\nlist -> ", response.content)
    #
    # def test_list(self):
    #     # response = responses.list_abacus(self.john)
    #     # print("\nlist -> ", response.content)
    #
    #     jsn = {'method' : 'list_abacus', 'data' : [[p.id, 'ntag', 'ndescriable', True, True] for p in Abacus.objects.filter(user=self.john) ]}
    #
    #     # c = client.Client()
    #     # self.client.post()
    #
    #     response = self.client.post('/api/abacus/action/', jsn)
    #     print(response.status_code, response.content)