from rest_framework.test import APITestCase


class Test(APITestCase):

    def test_install(self):
        from biohub.core.plugins import install, manager

        name = 'tests.core.plugins.my_plugin'
        install([name], migrate_database=True,
                migrate_options=dict(
                    test=True,
                    new_process=True))

        self.assertEqual(
            manager.plugin_infos[name],
            ('My Plugin', 'hsfzxjy', 'This is my plugin.'))

        resp = self.client.get('/api/my_plugin/')
        self.assertEqual(resp.data, [])
