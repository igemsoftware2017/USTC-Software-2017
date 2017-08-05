import json

from django.http import HttpResponse

from .models import Abacus
from ..abacus import aux_responses
from ..abacus import util

WRONG_OCCURRED_MSG = "Some wrong occurred,please ask administrator for help!"
STATE_IN_BLOCK_MSG = "Abacus state is not ready,please wait it finished or ask administrator for help!"

ACCESS_DENY_MSG = "Access denied!"
NONE_ABACUS_MSG = "No such abacus was found!"


def upload_file(user, jsn, files):
    data = jsn['data']
    ret_data = []
    loc = 0
    for (file, block) in zip(files, data):
        buf = [loc, -1, False, '']
        loc = loc + 1

        ret_data.append(buf)
        try:
            abacus = Abacus()
            abacus.user = user
            abacus.tag = block[0]
            abacus.descriable = block[1]
            abacus.shared = block[2]
            abacus.status = Abacus.TO_BE_START
            abacus.save()

            util.save_file(abacus.id, file)

            abacus.status = Abacus.UPLOADED
            abacus.save()

            if block[3] == True:
                abacus.status = Abacus.QUEUING
                abacus.save()
                aux_responses.calculate_service(abacus.id)
        except Exception:
            buf[3] = WRONG_OCCURRED_MSG
            continue

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

        abacus = Abacus.load(i)

        if abacus is None:
            buf[4] = NONE_ABACUS_MSG
            continue

        if user.id != abacus.user.id:
            buf[4] = ACCESS_DENY_MSG
            continue

        if util.get_file_path(i) is not None:
            buf[3] = "download/" + str(i)
        else:
            buf[3] = None

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

        abacus = Abacus.load(i)

        if abacus is None:
            buf[4] = NONE_ABACUS_MSG
            continue

        if user.id != abacus.user.id:
            buf[4] = ACCESS_DENY_MSG
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
        buf = [loc, id, False, -1, '']
        loc = loc + 1

        ret_data.append(buf)

        abacus = Abacus.load(i)

        if abacus is None:
            buf[4] = NONE_ABACUS_MSG
            continue

        if user.id != abacus.user.id:
            buf[4] = ACCESS_DENY_MSG
            continue

        try:
            util.delete_file(i)
            abacus.delete()
        except Exception:
            buf[4] = WRONG_OCCURRED_MSG
            continue

        buf[3] = 0
        buf[2] = True
        buf[1] = -1

    response_data = {}
    response_data['data'] = ret_data
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def edit_abacus(user, jsn, files):
    data = jsn['data']
    ret_data = []
    loc = 0
    for (file, block) in zip(files, data):
        buf = [loc, -1, False, '']
        loc = loc + 1

        ret_data.append(buf)

        try:
            abacus = Abacus.load(block[0])

            if abacus is None:
                buf[3] = NONE_ABACUS_MSG
                continue

            if user.id != abacus.user.id:
                buf[3] = ACCESS_DENY_MSG
                continue

            if file is not None:
                if abacus.status == Abacus.QUEUING:
                    buf[3] = STATE_IN_BLOCK_MSG
                    continue
                else:
                    abacus.status = Abacus.TO_BE_START
                    util.save_file(abacus.id, file)
                    abacus.status = Abacus.UPLOADED

            abacus.tag = block[1]
            abacus.descriable = block[2]
            abacus.shared = block[3]
            abacus.save()

            if block[4] == True:
                abacus.status = Abacus.QUEUING
                aux_responses.calculate_service(abacus.id)

            abacus.save()
        except Exception as e:
            print(e)
            buf[3] = WRONG_OCCURRED_MSG
            continue

        buf[1] = abacus.id
        buf[2] = True

    response_data = {}
    response_data['data'] = ret_data
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def list_abacus(user):
    quryset = Abacus.objects.filter(user=user)
    ret_data = []
    loc = 0
    for q in quryset:
        buf = [loc, q.id, True, q.status, q.tag, q.descriable, q.create_date, '']
        loc = loc + 1

        ret_data.append(buf)

    response_data = {}
    response_data['data'] = ret_data
    return HttpResponse(json.dumps(response_data, cls=util.DateTimeJsonEncoder), content_type="application/json")

def calculate(user, id):
    ret_data = []
    loc = 0
    for i in id:
        buf = [loc, -1, False, -1, '']
        loc = loc + 1

        ret_data.append(buf)

        abacus = Abacus.load(i)

        if abacus is None:
            buf[4] = NONE_ABACUS_MSG
            continue

        if user.id != abacus.user.id:
            buf[4] = ACCESS_DENY_MSG
            continue

        if abacus.status == Abacus.QUEUING:
            buf[4] = STATE_IN_BLOCK_MSG
            continue

        try:
            aux_responses.calculate_service(i)
            abacus.status = Abacus.QUEUING
            abacus.save()
        except Exception:
            buf[4] = WRONG_OCCURRED_MSG
            continue

        buf[3] = abacus.status
        buf[2] = True
        buf[1] = i

    response_data = {}
    response_data['data'] = ret_data
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def download_service(user, id):
    abacus = Abacus.load(id)

    if abacus is None:
        return HttpResponse(NONE_ABACUS_MSG)

    if user.id != abacus.user.id and not abacus.shared:
        return HttpResponse(ACCESS_DENY_MSG)

    return aux_responses.download_file_service(id)
