import os
from django.http import HttpResponse, Http404

from .models import Abacus
from .util import get_file_path
from .aux_calculate import CALCULATE_QUEUE

def calculate_service(user, id):
    CALCULATE_QUEUE.append(id)

def download_file_service(user, id):
    abacus = Abacus.objects.filter(id=id)

    if len(abacus) == 0:
        return HttpResponse("No such abacus was found!")

    abacus = abacus[0]

    if user.id != abacus.user.id and not abacus.shared:
        return HttpResponse("Access denied!")

    filepath_ = get_file_path(id)

    if filepath_ is None:
        return Http404()

    # 下载文件
    def readFile(fn, buf_size=262144):  # 大文件下载，设定缓存大小
        f = open(fn, "rb")
        while True:  # 循环读取
            c = f.read(buf_size)
            if c:
                yield c
            else:
                break
        f.close()

    response = HttpResponse(readFile(filepath_),
                            content_type='APPLICATION/OCTET-STREAM')  # 设定文件头，这种设定可以让任意文件都能正确下载，而且已知文本文件不是本地打开
    response['Content-Disposition'] = 'attachment; filename=' + "downloa.pdb"  # 设定传输给客户端的文件名称
    response['Content-Length'] = os.path.getsize(filepath_)  # 传输给客户端的文件大小
    return response
