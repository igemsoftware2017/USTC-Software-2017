from ._base import PluginTestCase
from biohub.core.plugins import plugins


class Test(PluginTestCase):

    def test_protect_install(self):
        name = 'tests.core.plugins.bad_plugin'
        with self.assertRaises(ZeroDivisionError):
            plugins.install([name],
                            update_config=True)

        self.assertNotIn(name, plugins.installed_apps)
        self.assertNotIn(name, plugins.available_plugins)
        self.assertNotIn(name, self.current_settings['PLUGINS'])
