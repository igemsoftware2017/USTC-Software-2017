import os
import tempfile
from .settings import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ['*']

LOGGING_DIR = os.getenv('BIOHUB_LOGGING_DIR', tempfile.gettempdir())
LOGGING_REQUEST_DIR = os.path.join(LOGGING_DIR, 'biohub_log', 'request')
LOGGING_ERROR_DIR = os.path.join(LOGGING_DIR, 'biohub_log', 'error')

os.makedirs(LOGGING_REQUEST_DIR, exist_ok=True)
os.makedirs(LOGGING_ERROR_DIR, exist_ok=True)


LOGGING = {
    "version": 1,
    "disable_existing_handlers": True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s:%(funcName)s:%(lineno)d %(process)d %(thread)x %(message)s',
            'level': 'WARNING'
        },
    },
    "handlers": {
        "error_log": {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_ERROR_DIR, 'log'),
            'formatter': 'verbose',
            'when': 'D'
        },
        'ignore': {
            'class': 'logging.NullHandler'
        }
    },
    "loggers": {
        'django': {
            'handlers': ['error_log'],
            'propagate': False,
            'level': 'WARNING',
        },
        'abacus_server': {
            'handlers': ['error_log'],
            'propagate': False,
            'level': 'WARNING',
        },
        '': {
            'handlers': ['error_log'],
            'propagate': False,
            'level': 'ERROR',
        },
        'daphne': {
            'handlers': ['ignore'],
            'propagate': False,
            'level': 'DEBUG'
        }
    }
}

del os
