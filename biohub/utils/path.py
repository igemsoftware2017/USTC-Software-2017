from importlib import import_module
from os.path import dirname, abspath, realpath


def filepath(filename):
    """
    Returns the exact directory where `filename` lies,
    following symlink.
    """
    return realpath(abspath(dirname(filename)))


def modpath(modname):
    """
    Returns the exact directory of a package.
    """
    return filepath(import_module(modname).__file__)
