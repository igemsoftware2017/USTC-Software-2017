import json

from rest_framework.test import APITestCase
from biohub.core.plugins import plugins
from biohub.core.conf import settings


class PluginTestCase(APITestCase):

    def setUp(self):
        self._protect = plugins.protect(test=True, config=True)
        self._protect.acquire()

    def tearDown(self):
        self._protect.release()

    @property
    def current_settings(self):

        with open(settings.config_file_path, 'r') as fp:
            data = json.load(fp)

        return data
