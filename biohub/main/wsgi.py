"""
WSGI config for biohub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import biohub.compat  # noqa

from django.core.wsgi import get_wsgi_application

try:
    import biohub  # noqa: F401
except ImportError:
    import sys
    from os import path, dirname
    sys.path.insert(
        0,
        path.join(dirname(__file__), '..', '..'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biohub.settings")

application = get_wsgi_application()
