import os
import subprocess

from ._base import PluginTestCase

config_modifier_code = """
import os
import json

fn = os.environ['BIOHUB_CONFIG_PATH']
with open(fn, 'r') as f:
    data = json.load(f)
data['PLUGINS'] = ['tests.core.plugins.my_plugin']
with open(fn, 'w') as f:
    json.dump(data, f)
"""


class Test(PluginTestCase):

    def test_reload(self):
        self.assertEqual(
            self.client.get('/api/my_plugin/hello/').status_code,
            404
        )

        subprocess.Popen(['python', '-c', config_modifier_code]).communicate()
        subprocess.Popen(['kill', '-USR1', str(os.getpid())]).communicate()

        from biohub.core.plugins import plugins
        self.assertGreater(len(plugins.plugin_infos), 0)

        self.assertEqual(
            self.client.get('/api/my_plugin/hello/').data,
            'Hello'
        )
