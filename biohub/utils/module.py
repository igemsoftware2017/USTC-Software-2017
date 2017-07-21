import importlib
import importlib.util

module_from_path = importlib.import_module


def object_from_path(value):
    """
    Given a dot-separated path and returns the referred object.

    (e.g. 'math.PI')
    """
    path, obj_name = value.rsplit('.', 1)
    module = module_from_path(path)

    return getattr(module, obj_name)


def is_valid_module_path(value, try_import=False):
    """
    Check if the given `path` is a valid dot-separated python module path.

    By default, this function will NOT try to import the module, unless the
    flag `try_import` is set to True.
    """
    result = all(s.isidentifier() for s in value.split('.'))

    if result and try_import:
        try:
            importlib.import_module(value)

            return True
        except ModuleNotFoundError:
            return False

    return result


def module_from_file_location(filename):
    """
    Reference: https://stackoverflow.com/questions/67631/
    Load and return a module object with the given file name.
    """
    spec = importlib.util.spec_from_file_location('__tmp__', filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
