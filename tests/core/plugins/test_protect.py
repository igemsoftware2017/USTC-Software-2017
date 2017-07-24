from ._base import PluginTestCase
from biohub.core.plugins import manager


class Test(PluginTestCase):

    def test_protect_install(self):
        name = 'tests.core.plugins.bad_plugin'
        with self.assertRaises(ZeroDivisionError):
            manager.install([name],
                            update_config=True)

        self.assertNotIn(name, manager.installed_apps)
        self.assertNotIn(name, manager.available_plugins)
        self.assertNotIn(name, self.current_settings['PLUGINS'])
