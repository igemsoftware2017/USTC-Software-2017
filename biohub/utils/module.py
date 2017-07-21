import importlib
import importlib.util

from django.utils.module_loading import module_has_submodule

module_from_path = importlib.import_module


def autodiscover_modules(*args, force_reload=True):
    """
    An enhanced version of `django.utils.module_loading.autodiscover_modules`,
    which can force target modules to be reloaded.
    """

    from django.apps import apps
    import sys

    for app_config in apps.get_app_configs():
        for module_to_search in args:
            mod_name = '%s.%s' % (app_config.name, module_to_search)

            if force_reload:
                try:
                    del sys.modules[mod_name]
                except KeyError:
                    pass

            try:
                importlib.import_module(mod_name)
            except Exception:
                if module_has_submodule(app_config.module, module_to_search):
                    raise


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
