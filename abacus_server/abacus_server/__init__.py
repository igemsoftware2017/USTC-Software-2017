from .celery import app as celery_app
from . import tasks  # noqa

__all__ = ['celery_app']
