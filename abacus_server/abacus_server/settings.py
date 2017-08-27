import os
import json
import subprocess

# Make sure java is available
p = subprocess.Popen(['java', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
p.communicate()

if p.returncode != 0:
    raise RuntimeError('Cannot access command `java`, make sure it\'s properly installed.')
else:
    del p, subprocess


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '*+cxzm4-ou5!mv^3l*qm5e)$(3!s8#!vyj%5csb98&i-ml4rj='

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'abacus_server.urls'

WSGI_APPLICATION = 'abacus_server.wsgi.application'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True

STATIC_URL = '/static/'

FILE_UPLOAD_HANDLERS = [
    'abacus_server.file_handlers.StraightHandler'
]

MEDIA_URL = '/media/'


# Load custom settings from config.json

try:
    with open(os.path.join(BASE_DIR, 'config.json'), 'r') as f:
        CONFIGS = json.load(f)
except FileNotFoundError:
    CONFIGS = {}


def extract_config_item(name, default, validation, assertion):

    result = os.environ.get(name, CONFIGS.get(name, default))
    assert validation(result), assertion.format(result)

    return result


ABACUS_JAR_PATH = extract_config_item(
    'ABACUS_JAR_PATH',
    '',
    os.path.isfile,
    'ABACUS_JAR_PATH {value} should point to a jar file.'
)

ABACUS_DATABASE_PATH = extract_config_item(
    'ABACUS_DATABASE_PATH',
    '',
    os.path.isfile,
    'ABACUS_DATABASE_PATH {value} should point to a txt file.')

REDIS_URI = extract_config_item(
    'REDIS_URI',
    None,
    lambda v: isinstance(v, str),
    'REDIS_URI {value} should be a string.'
)

MEDIA_ROOT = extract_config_item(
    'STORAGE_ROOT',
    '/tmp/abacus/',
    lambda v: isinstance(v, str),
    'STORAGE_ROOT {value} should be a string.'
)

ABACUS_BASE_ARGUMENTS = [
    'java',
    '-jar',
    ABACUS_JAR_PATH,
    '-design',
    '-dir', ABACUS_DATABASE_PATH
]


CELERY_BROKER_URL = REDIS_URI
CELERY_RESULT_BACKEND = REDIS_URI
