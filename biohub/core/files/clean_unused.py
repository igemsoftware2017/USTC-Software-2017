import re
import os
import warnings
from functools import reduce
from operator import add

from django.conf import settings
from django.apps import apps
from django.core.files.storage import default_storage
from django.core.cache import cache

PREFIX = '__cleanunused__'


def _make_key(name):
    return '{}{}'.format(PREFIX, name)


def _fields_to_search():
    """
    Yields a list of (model_class, config) tuples. Each `config` is a dict
    mapping field_names to their matching regular expressions.
    """

    for ac in apps.app_configs.values():
        if not hasattr(ac, 'clean_unused'):
            continue

        label = ac.label
        for model_name, config in ac.clean_unused:
            yield (apps.get_model(label, model_name), config)


def _resolve_referenced_files(config):
    """
    Fetches and analyzes the whole database, figures out and caches referenced
    files.
    """

    # Clear unexpired caches
    cache.delete_pattern(PREFIX)

    for model, fields in config:
        fields_to_fetch = set(fields.keys()) & {'id'}

        instances = model.objects.values(*fields_to_fetch)

        re_objects = [(field_name, re.compile(regexp))
                      for field_name, regexp in fields.items()]

        for instance in instances:

            # Use RegExp to extract the file names
            files_found = reduce(
                add,
                (re.findall(exp, instance[fname])
                 for fname, exp in re_objects))

            for file in files_found:

                # Interpret into file name if it's URL
                if file.startswith(settings.MEDIA_URL):
                    file = file[len(settings.MEDIA_URL):]

                # Cache up the file name
                cache.set(_make_key(file), 1, timeout=86400)


def clean_unused():
    """
    A function to clear unreferenced media files.
    """

    if not hasattr(cache, 'delete_pattern'):
        # Abort if cache backend is not redis
        warnings.warn(
            'Unused files clearing aborted due to bad cache backend settings.')
        return

    _resolve_referenced_files(_fields_to_search())

    with os.scandir(settings.MEDIA_ROOT) as iterator:

        for entry in iterator:

            name = entry.name

            if not entry.is_file() or\
                    cache.get(_make_key(name)) is not None:
                continue

            default_storage.delete(name)
