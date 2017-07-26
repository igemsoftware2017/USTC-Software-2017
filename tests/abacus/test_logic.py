from rest_framework.test import APITestCase
from django.http import Http404

from biohub.accounts.models import User
from biohub.abacus.models import Abacus
from biohub.abacus import responses


class AbacusTestCase(APITestCase):

    def setUp(self):
        self.john = User.objects.create_user(username='john', password='password')
        self.lili = User.objects.create_user(username='lili', password='password')

class TestUpload(AbacusTestCase):
    # def test_upload(self):
    #     data = ['tag', 'describle', True, True]
    #     file = open("biohub/abacus/storage/download/download.pdb")
    #
    #     jsn = {'data': [data, data, data, ], }
    #     files = [file, file, file, ]
    #
    #     response = response_tool.upload_file(self.john, jsn, files)
    #     print("\nupload -> ", response.content)

    # def test_list_abacus(self):
    #     response = response_tool.list_abacus(self.john)
    #     print("\nlist -> ", response.content)

    # def test_delete_abacus(self):
    #     data = ['tag', 'describle', True, True]
    #     file = open("biohub/abacus/storage/download/download.pdb")
    #
    #     jsn = {'data': [data, data, data, ], }
    #     files = [file, file, file, ]
    #
    #     response = response_tool.upload_file(self.john, jsn, files)
    #     print("\nupload -> ", response.content)
    #
    #     # test normaol
    #     # response = response_tool.delete_file(self.john, [p.id for p in Abacus.objects.filter(user=self.john)])
    #     # print("delete -> ", response.content)
    #
    #     # test no such files
    #     # response = response_tool.delete_file(self.john, [(10 * p.id) for p in Abacus.objects.filter(user=self.john)])
    #     # print("delete -> ", response.content)
    #
    #     # test access denied
    #     response = response_tool.delete_file(self.lili, [(p.id) for p in Abacus.objects.filter(user=self.john)])
    #     print("delete -> ", response.content)

    # def test_edit(self):
    #     data = ['tag', 'describle', True, True]
    #     file = open("biohub/abacus/storage/download/download.pdb")
    #
    #     jsn = {'data': [data, data, data, ], }
    #     files = [file, file, file, ]
    #
    #     response = response_tool.upload_file(self.john, jsn, files)
    #     print("\nupload -> ", response.content)
    #
    #     # test normal
    #     # jsn = {'data' : [[p.id, 'ntag', 'ndescriable', True, True] for p in Abacus.objects.filter(user=self.john) ]}
    #     # response = response_tool.edit_abacus(self.john, jsn, files)
    #     # print("\nedit -> ", response.content)
    #     # response = response_tool.list_abacus(self.john)
    #     # print("\nlist -> ", response.content)
    #
    #     # test normal without files
    #     # jsn = {'data' : [[p.id, 'ntag', 'ndescriable', True, True] for p in Abacus.objects.filter(user=self.john) ]}
    #     # response = response_tool.edit_abacus(self.john, jsn, [None for p in Abacus.objects.filter(user=self.john)])
    #     # print("\nedit -> ", response.content)
    #     # response = response_tool.list_abacus(self.john)
    #     # print("\nlist -> ", response.content)
    #
    #     # test access denied
    #     # jsn = {'data' : [[p.id, 'ntag', 'ndescriable', True, True] for p in Abacus.objects.filter(user=self.john) ]}
    #     # response = response_tool.edit_abacus(self.lili, jsn, files)
    #     # print("\nedit -> ", response.content)
    #     # response = response_tool.list_abacus(self.john)
    #     # print("\nlist -> ", response.content)

    # def test_get_download_file(self):
    #
    #     data = ['tag', 'describle', True, True]
    #     file = open("biohub/abacus/storage/download/download.pdb")
    #
    #     jsn = {'data': [data, data, data, ], }
    #     files = [file, file, file, ]
    #
    #     response = response_tool.upload_file(self.john, jsn, files)
    #     print("\nupload -> ", response.content)
    #
    #     response = response_tool.get_download_file(self.john, [p.id for p in Abacus.objects.filter(user=self.john)])
    #     print("\ngetDownloadFile -> ", response.content)

    def test_download_file(self):
        data = ['tag', 'describle', True, True]
        file = open("biohub/abacus/storage/download/download.pdb")

        jsn = {'data': [data, data, data, ], }
        files = [file, file, file, ]

        response = responses.upload_file(self.john, jsn, files)
        print("\nupload -> ", response.content)

        response = responses.download_service(self.john, 1)
        print("\ngetDownloadFile -> ", response)

        from time import sleep
        while True:
            sleep(100)
