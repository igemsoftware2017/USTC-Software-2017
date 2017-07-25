import os

from .apps import AbacusConfig


STORAGE_PATH = os.path.join(AbacusConfig.app_path, 'storage/')

def copyfileobj_example(source, dest, buffer_size=1024*1024):
    while 1:
        copy_buffer = source.read(buffer_size)
        if not copy_buffer:
            break
        dest.write(copy_buffer)

def save_file(id, file):
    if not os.path.exists(STORAGE_PATH):
        os.makedirs(STORAGE_PATH)

    target_path = os.path.join(STORAGE_PATH, 'upload/' + str(id) + '.pdb')
    copyfileobj_example(file, open(target_path, 'w+'))

def delete_file(id):
    file_path = os.path.join(STORAGE_PATH, 'download/' + str(id) + '.zip')
    if not os.path.exists(file_path):
        return

    os.remove(file_path)

def get_file_path(id):
    file_path = os.path.join(STORAGE_PATH, 'download/' + str(id) + '.zip')
    if not os.path.exists(file_path):
        return None

    return file_path
