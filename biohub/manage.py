#!/usr/bin/env python

import compat  # noqa: F401

import os
import sys

from os.path import dirname, join, abspath, realpath


if __name__ == "__main__":

    CURRENT_DIR = abspath(dirname(realpath(__file__)))
    BIOHUB_BASE_DIR = join(CURRENT_DIR, '..')

    try:
        import biohub  # noqa: F401
    except ImportError:
        sys.path.insert(0, BIOHUB_BASE_DIR)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biohub.main.settings.dev")
    os.environ.setdefault("BIOHUB_CONFIG_PATH",
                          join(BIOHUB_BASE_DIR, 'config.json'))
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django  # noqa: F401
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
