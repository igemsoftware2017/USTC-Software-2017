from ._base import PluginTestCase

from biohub.core.conf import manager as settings_manager


class Test(PluginTestCase):

    def setUp(self):
        settings_manager.store_settings()

    def tearDown(self):
        settings_manager.restore_settings()

    def test_remove(self):
        from biohub.core.plugins import install, remove, manager
        from django.apps import apps

        name = 'tests.core.plugins.my_plugin'

        # Phase 1
        install([name], migrate_database=True, update_config=True,
                migrate_options=dict(
                    test=True,
                    new_process=True))

        self.assertIn(name, self.current_settings['PLUGINS'])
        self.assertIn(name, manager.plugin_infos)
        self.assertTrue(apps.is_installed(name))

        # Phase 2
        remove([name], update_config=True)

        resp = self.client.get('/api/my_plugin/')
        self.assertNotIn(name, self.current_settings['PLUGINS'])

        self.assertEqual(resp.status_code, 404)
        self.assertNotIn(name, manager.plugin_infos)
        self.assertFalse(apps.is_installed(name))

        # Phase 3
        install([name], migrate_database=True, update_config=True,
                migrate_options=dict(
                    test=True,
                    new_process=True))

        self.assertIn(name, self.current_settings['PLUGINS'])

        # Phase 4
        remove([name], update_config=True)

        self.assertNotIn(name, self.current_settings['PLUGINS'])
        self.assertNotIn(name, manager.plugin_infos)
