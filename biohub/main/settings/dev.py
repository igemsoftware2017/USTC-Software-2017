from .base import *  # noqa
import coloredlogs

ALLOWED_HOSTS = ['*']

TIME_ZONE = 'Asia/Shanghai'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'colored_formatter': {
            '()': coloredlogs.ColoredFormatter,
            'format': '%(name)s:%(funcName)s:%(lineno)d %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored_formatter'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False
        },
        'filelock': {
            'handlers': ['console'],
            'level': 'CRITICAL',
            'propagate': False
        },
        '': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True
        }
    }
}

DEBUG = True
