import json

from rest_framework.test import APITestCase

from biohub.core.conf import manager as settings_manager


class Test(APITestCase):

    def setUp(self):
        settings_manager.store_settings()

    def tearDown(self):
        settings_manager.restore_settings()

    def test_remove(self):
        from biohub.core.plugins import install, remove, manager
        from django.apps import apps

        name = 'tests.core.plugins.my_plugin'
        install([name], migrate_database=True, update_config=True,
                migrate_options=dict(
                    test=True,
                    new_process=True))

        with open(settings_manager.config_file_path, 'r') as fp:
            data = json.load(fp)

            self.assertIn(name, data['PLUGINS'])

        self.assertIn(name, manager.plugin_infos)
        self.assertTrue(apps.is_installed(name))

        remove([name], update_config=True)

        resp = self.client.get('/api/my_plugin/')
        self.assertEqual(resp.status_code, 404)

        with open(settings_manager.config_file_path, 'r') as fp:
            data = json.load(fp)

            self.assertNotIn(name, data['PLUGINS'])

        self.assertNotIn(name, manager.plugin_infos)

        self.assertNotIn(name, manager.plugin_infos)
        self.assertFalse(apps.is_installed(name))

        install([name], migrate_database=True, update_config=True,
                migrate_options=dict(
                    test=True,
                    new_process=True))

        with open(settings_manager.config_file_path, 'r') as fp:
            data = json.load(fp)

            self.assertIn(name, data['PLUGINS'])

        remove([name], update_config=True)

        with open(settings_manager.config_file_path, 'r') as fp:
            data = json.load(fp)

            self.assertNotIn(name, data['PLUGINS'])

        self.assertNotIn(name, manager.plugin_infos)
