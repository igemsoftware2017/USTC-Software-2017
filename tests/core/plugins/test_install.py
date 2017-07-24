from ._base import PluginTestCase


class Test(PluginTestCase):

    def test_install(self):
        from biohub.core.plugins import install, manager

        name = 'tests.core.plugins.my_plugin'

        # Phase 1
        install([name], migrate_database=True, update_config=True,
                migrate_options=dict(
                    test=True,
                    new_process=True))

        self.assertIn(name, self.current_settings['PLUGINS'])
        self.assertEqual(
            manager.plugin_infos[name],
            ('My Plugin', 'hsfzxjy', 'This is my plugin.'))

        # Phase 2
        install(['tests.core.plugins.another_plugin'],
                migrate_database=True, update_config=True,
                migrate_options=dict(
                    test=True,
                    new_process=True))

        resp = self.client.get('/api/another_plugin/')
        self.assertEqual(resp.data, [])
        resp = self.client.get('/api/my_plugin/')
        self.assertEqual(resp.data, [])
