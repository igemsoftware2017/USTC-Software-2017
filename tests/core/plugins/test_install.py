import json

from rest_framework.test import APITestCase

from biohub.core.conf import manager as settings_manager


class Test(APITestCase):

    def setUp(self):
        settings_manager.store_settings()

    def tearDown(self):
        settings_manager.restore_settings()

    def test_install(self):
        from biohub.core.plugins import install, manager, remove

        name = 'tests.core.plugins.my_plugin'
        install([name], migrate_database=True, update_config=True,
                migrate_options=dict(
                    test=True,
                    new_process=True))

        with open(settings_manager.config_file_path, 'r') as fp:
            data = json.load(fp)

            self.assertIn(name, data['PLUGINS'])

        self.assertEqual(
            manager.plugin_infos[name],
            ('My Plugin', 'hsfzxjy', 'This is my plugin.'))

        install(['tests.core.plugins.another_plugin'],
                migrate_database=True, update_config=True,
                migrate_options=dict(
                    test=True,
                    new_process=True))

        resp = self.client.get('/api/another_plugin/')
        self.assertEqual(resp.data, [])

        resp = self.client.get('/api/my_plugin/')
        self.assertEqual(resp.data, [])

        remove(['tests.core.plugins.another_plugin', name])
