from __future__ import absolute_import

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abacus_server.settings')

app = Celery('abacus_server')
app.config_from_object('django.conf:settings', namespace='CELERY')
