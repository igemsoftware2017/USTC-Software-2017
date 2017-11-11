import importlib
import os
from ._base import PluginTestCase


class Test(PluginTestCase):

    def write(self, string):

        dir = os.path.dirname(__file__)
        with open(dir + '/my_plugin/consts.py', 'w') as f:
            f.write('String = \'{}\'\n'.format(string))

    def tearDown(self):
        super(PluginTestCase, self).tearDown()
        self.write('Hello')

    def test_refresh(self):
        from biohub.core.plugins import install, remove, plugins
        from django.apps import apps

        name = 'tests.core.plugins.my_plugin'

        # Phase 1
        install([name], migrate_database=True, update_config=True,
                migrate_options=dict(
                    test=True,
                    new_process=True))

        self.assertIn(name, self.current_settings['PLUGINS'])
        self.assertIn(name, plugins.plugin_infos)
        self.assertTrue(apps.is_installed(name))

        self.assertEqual(
            self.client.get('/api/my_plugin/hello/').data,
            'Hello'
        )

        # Phase patch
        self.write('Patching')
        plugins.refresh_plugins([name])

        self.assertEqual(
            importlib.import_module('tests.core.plugins.my_plugin.consts').String,
            'Patching'
        )

        # Phase 2
        remove([name], update_config=True)

        self.assertNotIn(name, self.current_settings['PLUGINS'])
        self.assertNotIn(name, plugins.plugin_infos)
