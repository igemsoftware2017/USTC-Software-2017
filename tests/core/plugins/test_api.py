from ._base import PluginTestCase
from biohub.core.plugins import install

from django.urls import reverse


class Test(PluginTestCase):

    def test_list(self):
        name = 'tests.core.plugins.my_plugin'
        install([name], update_config=True)

        resp = self.client.get(reverse('api:plugins:list'))

        self.assertIn({
            'name': name,
            'author': 'hsfzxjy',
            'title': 'My Plugin',
            'description': 'This is my plugin.'
        }, resp.data)
