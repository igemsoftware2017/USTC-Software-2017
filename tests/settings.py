from biohub.main.settings.dev import *

test_apps = ['tests.core.files.cleanunused_tests']
INSTALLED_APPS += list(set(test_apps) - set(INSTALLED_APPS))
