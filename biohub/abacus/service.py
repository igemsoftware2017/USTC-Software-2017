import os
from django.http import HttpResponse

from .models import Abacus
from .file_tool import get_file_path

def is_self_abacus(user, id):
    abacus = Abacus.objects.filte(id=id)

    if abacus is None:
        return False

    if user.id != abacus.user.id:
        return False

    return True

def is_access_abacus(user, id):
    abacus = Abacus.objects.filte(id=id)

    if abacus is None:
        return False

    if user.id != abacus.user.id and not abacus.shared:
        return False

    return True

def download_file_service(user, id):
    abacus = Abacus.objects.filte(id=id)

    if abacus is None:
        return HttpResponse("No such abacus was found!")

    if user.id != abacus.user.id and not abacus.shared:
        return HttpResponse("Access denied!")

    filepath_ = get_file_path(id)

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

def calculate(user, id):
    abacus = Abacus.objects.filte(id=id)

    if abacus is None:
        return HttpResponse("No such abacus was found!")

    if user.id != abacus.user.id and not abacus.shared:
        return HttpResponse("Access denied!")

    print("calculating...")
    return HttpResponse("Calculating...")
