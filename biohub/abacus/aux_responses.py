import os

from django.http import HttpResponse, Http404

from .util import get_file_path
from ..abacus import aux_calculate


def calculate_service(id):
    aux_calculate.calculate(id)

def download_file_service(id):
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
