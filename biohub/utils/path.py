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
    return filepath(__import__(modname).__file__)
