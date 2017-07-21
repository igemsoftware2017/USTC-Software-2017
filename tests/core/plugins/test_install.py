from rest_framework.test import APITestCase

from biohub.core.conf import manager as settings_manager


class Test(APITestCase):

    def setUp(self):
        settings_manager.store_settings()

    def tearDown(self):
        settings_manager.restore_settings()

    def test_install(self):
        from biohub.core.plugins import install, manager

        name = 'tests.core.plugins.my_plugin'
        install([name], migrate_database=True, update_config=True,
                migrate_options=dict(
                    test=True,
                    new_process=True))

        self.assertEqual(
            manager.plugin_infos[name],
            ('My Plugin', 'hsfzxjy', 'This is my plugin.'))

        resp = self.client.get('/api/my_plugin/')
        self.assertEqual(resp.data, [])
