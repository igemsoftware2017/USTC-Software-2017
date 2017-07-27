import os.path as path

current_dir = path.dirname(__file__)


def open_sample(name, mode='rb'):

    return open(path.join(current_dir, 'samples', name), mode)
