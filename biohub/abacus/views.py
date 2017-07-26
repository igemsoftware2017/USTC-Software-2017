import json

from django.shortcuts import render
from rest_framework import viewsets, decorators

from ..abacus import responses


class AbacusView(
        viewsets.GenericViewSet):

    def list_abacus(self):
        return responses.list_abacus(self.request.user)

    def get_status(self, id):
        return responses.get_status(self.request.user, id)

    def get_download_file(self, id):
        return responses.get_download_file(self.request.user, id)

    def upload_file(self, jsn, files):
        return responses.upload_file(self.request.user, jsn, files)

    def delete_file(self, id):
        return responses.delete_file(self.request.user, id)

    def calculate(self, id):
        return responses.calculate(self.request.user, id)

    def edit_abacus(self, jsn, files):
        return responses.edit_abacus(self.request.user, jsn, files)

    @decorators.list_route(methods=['GET'])
    def download(self, request):
        return responses.download_service(self.request.user, request['id'])

    @decorators.list_route()
    def upload(self, request):
        return self.upload_file(json.load(request.body), request.FILES.getlist('files'))

    @decorators.list_route()
    def edit(self, request):
        return self.edit_abacus(json.load(request.body), request.FILES.getlist('files'))

    @decorators.list_route()
    def action(self, request):
        # request.POST.
        jsn = json.load(request.body)
        method = jsn['method']
        id = jsn['data']

        if method == "get_download_file":
            return self.get_download_file(id)
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
