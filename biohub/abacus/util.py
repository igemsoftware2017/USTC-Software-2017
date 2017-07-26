import json
import datetime

import os

# from .apps import AbacusConfig
# STORAGE_PATH = os.path.join(AbacusConfig.app_path, 'storage/')


class DateTimeJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, o)

STORAGE_PATH = os.path.join(os.getcwd(), 'storage/abacus/')
UPLOAD_PATH = os.path.join(STORAGE_PATH, 'upload/')
DOWNLOAD_PATH = os.path.join(STORAGE_PATH, 'download/')

def copyfileobj_example(source, dest, buffer_size=1024*1024):
    while 1:
        copy_buffer = source.read(buffer_size)
        if not copy_buffer:
            break
        dest.write(copy_buffer)

def save_file(id, file):
    if not os.path.exists(UPLOAD_PATH):
        os.makedirs(UPLOAD_PATH)

    target_path = os.path.join(UPLOAD_PATH, str(id) + '.pdb')
    copyfileobj_example(file, open(target_path, 'w+'))

def delete_file(id):
    file_path = os.path.join(UPLOAD_PATH, str(id) + '.zip')
    if not os.path.exists(file_path):
        pass
    else:
        os.remove(file_path)

    file_path = os.path.join(DOWNLOAD_PATH, str(id) + '.zip')
    if not os.path.exists(file_path):
        pass
    else:
        os.remove(file_path)

def get_file_path(id):
    file_path = os.path.join(DOWNLOAD_PATH, str(id) + '.zip')
    if not os.path.exists(file_path):
        return None

    return file_path