"""
WSGI config for biohub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
from os import path
import biohub.compat  # noqa

from django.core.wsgi import get_wsgi_application

try:
    import biohub  # noqa: F401
except ImportError:
    import sys
    sys.path.insert(
        0,
        path.join(path.dirname(__file__), '..', '..'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biohub.settings")
os.environ.setdefault('BIOHUB_CONFIG_PATH', path.join(path.dirname(__file__), '..', '..', 'config.json'))

application = get_wsgi_application()
