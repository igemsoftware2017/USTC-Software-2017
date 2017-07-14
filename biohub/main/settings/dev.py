from .base import *  # noqa: F403,F401
import coloredlogs

import os

TIME_ZONE = 'Asia/Shanghai'

os.environ.setdefault(
    'COLOREDLOGS_LOG_FORMAT',
    '%(name)s:%(funcName)s:%(lineno)d %(message)s'
)
os.environ.setdefault(
    'COLOREDLOGS_FIELD_STYLES',
    'name=green,bold',
)

coloredlogs.install('DEBUG')

DEBUG = True
