import json

from django.http import HttpResponse

from .models import Abacus
from ..abacus import service
from ..abacus import file_tool

def upload_file(user, jsn, files):
    data = jsn['data']
    ret_data = []
    loc = 0
    for (file, block) in zip(files, data):
        buf = [loc, -1, False, None]
        ret_data.append(buf)
        try:
            abacus = Abacus()
            abacus.user = user
            abacus.tag = block[0]
            abacus.descriable = block[1]
            abacus.shared = block[2]
            abacus.status = 0
            abacus.save()

            file_tool.save_file(abacus.id, file)
            if block[3] == True:
                abacus.status = 1
                abacus.save()
                service.calculate(user, abacus.id)
        except Exception:
            buf[3] = "Some wrong occurred,please try again later or ask administrator for help!"

        buf[1] = abacus.id
        buf[2] = True

    response_data = {}
    response_data['data'] = ret_data
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_download_file(user, id):
    ret_data = []
    loc = 0
    for i in id:
        buf = [loc, -1, False, None, '']
        loc = loc + 1

        ret_data.append(buf)

        abacus = Abacus.objects.filte(id=i)

        if abacus is None:
            buf[4] = "No such abacus was found!"
            continue

        if user.id != abacus.user.id and not abacus.shared:
            buf[4] = "Access denied!"
            continue

        buf[3] = file_tool.get_file_path(i)
        buf[2] = True
        buf[1] = i

    response_data = {}
    response_data['data'] = ret_data
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_status(user, id):
    ret_data = []
    loc = 0
    for i in id:
        buf = [loc, -1, False, -1, '']
        loc = loc + 1

        ret_data.append(buf)

        abacus = Abacus.objects.filte(id=i)

        if abacus is None:
            buf[4] = "No such abacus was found!"
            continue

        if user.id != abacus.user.id and not abacus.shared:
            buf[4] = "Access denied!"
            continue

        buf[3] = abacus.status
        buf[2] = True
        buf[1] = i

    response_data = {}
    response_data['data'] = ret_data
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def delete_file(user, id):
    ret_data = []
    loc = 0
    for i in id:
        buf = [loc, -1, False, -1, '']
        loc = loc + 1

        ret_data.append(buf)

        abacus = Abacus.objects.filte(id=i)

        if abacus is None:
            buf[4] = "No such abacus was found!"
            continue

        if user.id != abacus.user.id and not abacus.shared:
            buf[4] = "Access denied!"
            continue

        try:
            delete_file(id)
            abacus.delete()
        except Exception:
            buf[4] = "On delete file, exception occurred.Please try again later or ask administrator for help!"
            continue

        buf[2] = True
        buf[1] = -1

    response_data = {}
    response_data['data'] = ret_data
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def edit_file(user, jsn, files):
    data = jsn['data']
    ret_data = []
    loc = 0
    for (file, block) in zip(files, data):
        buf = [loc, -1, False, None]
        ret_data.append(buf)
        try:
            abacus = Abacus.objects.filte(id=block[0])
            abacus.tag = block[1]
            abacus.descriable = block[2]
            abacus.shared = block[3]
            abacus.save()

            if file is not None:
                abacus.status = 0
                file_tool.save_file(abacus.id, file)
                abacus.status = 1

            if block[4] == True:
                abacus.status = 1
                calculate(user, abacus.id)

            abacus.save()
        except Exception:
            buf[3] = "Some wrong occurred,please try again later or ask administrator for help!"

        buf[1] = abacus.id
        buf[2] = True

    response_data = {}
    response_data['data'] = ret_data
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def list_abacus(user):
    quryset = Abacus.objects.filte(user=user)
    ret_data = []
    for count,q in quryset:
        buf = [count, q.id, True, q.status, q.tag, q.describle, q.create_date, '']
        ret_data.append(buf)

    response_data = {}
    response_data['data'] = ret_data
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def calculate(user, id):
    ret_data = []
    loc = 0
    for i in id:
        buf = [loc, -1, False, -1, '']
        loc = loc + 1

        ret_data.append(buf)

        abacus = Abacus.objects.filte(id=i)

        if abacus is None:
            buf[4] = "No such abacus was found!"
            continue

        if user.id != abacus.user.id and not abacus.shared:
            buf[4] = "Access denied!"
            continue

        try:
            service.calculate(user, id)
            abacus.status = 1
        except Exception:
            buf[4] = "Exception occurred.Please try again later or ask administrator for help!"
            continue

        buf[2] = True
        buf[1] = -1

    response_data = {}
    response_data['data'] = ret_data
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def download_service(user, id):
    return service.download_file_service(user, id)
