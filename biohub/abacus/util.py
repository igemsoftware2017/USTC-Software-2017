import json
import datetime

import os


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

def copy_file(source, dest, buffer_size=1024 * 1024):
    while True:
        copy_buffer = source.read(buffer_size)
        if not copy_buffer:
            break
        dest.write(copy_buffer)

def generate_upload_path(id):
    return os.path.join(UPLOAD_PATH, str(id) + '.pdb')

def generate_download_path(id):
    return os.path.join(DOWNLOAD_PATH, str(id) + '.zip')

def save_upload_file(id, file):
    if not os.path.exists(UPLOAD_PATH):
        os.makedirs(UPLOAD_PATH)

    target_path = generate_upload_path(id)
    copy_file(file, open(target_path, 'wb+'))

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)
        return True

    return False

def delete_abacus_file(id):
    file_path = generate_upload_path(id)
    delete_file(file_path)

    file_path = generate_download_path(id)
    delete_file(file_path)

def get_file_path(path):
    if os.path.exists(path):
        return path

    return None

def get_download_file_path(id):
    path = generate_download_path(id)
    return get_file_path(path)

def get_upload_file_path(id):
    path = generate_upload_path(id)
    return get_file_path(path)