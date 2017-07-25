import json

from django.shortcuts import render
from rest_framework import viewsets, decorators

from ..abacus import response_tool


class AbacusView(
        viewsets.GenericViewSet):

    filter_fields = ('tag', 'upload_file')

    def list_abacus(self):
        return response_tool.list_abacus(self.request.user)

    def get_status(self, id):
        return response_tool.get_status(self.request.user, id)

    def download_file(self, id):
        return response_tool.get_download_file(self.request.user, id)

    def upload_file(self, jsn, files):
        return response_tool.upload_file(self.request.user, jsn, files)

    def delete_file(self, id):
        return response_tool.delete_file(self.request.user, id)

    def calculate(self, id):
        return response_tool.calculate(self.request.user, id)

    @decorators.list_route(methods=['GET'])
    def download(self, request):
        return response_tool.download_service(self.request.user, request['id'])

    @decorators.list_route()
    def action(self, request):
        # request.POST.
        jsn = json.load(request.body)
        method = jsn['method']
        id = jsn['data']

        if method == "download_file":
            return self.download_file(id)
        elif method == "get_status":
            return self.get_status(id)
        elif method == "list_abacus":
            return self.list_abacus()
        elif method == "delete_file":
            return self.delete_file(id)
        elif method == "calculate":
            return self.calculate(id)
        else:
            return
        pass

    @decorators.list_route(methods=['Get', 'Post'])
    def index(self, request):
        return render(request, 'abacus.html')
