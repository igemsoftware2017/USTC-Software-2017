from importlib import import_module
from os.path import dirname, abspath, realpath, expanduser
from os.path import join  # noqa


def filepath(filename):
    """
    Returns the exact directory where `filename` lies, following symlinks.
    """
    return realdir(dirname(filename))


def realdir(dirname):
    """
    Expand the given directory to an absolute one, following symlinks.
    """

    return realpath(abspath(expanduser(dirname)))


def modpath(modname):
    """
    Returns the exact directory of a package.
    """
    return filepath(import_module(modname).__file__)
