from ._base import PluginTestCase


class Test(PluginTestCase):

    def tearDown(self):
        from biohub.core.plugins.user_plugin_manager import redis_storage
        from biohub.core.plugins import plugins

        plugins.remove(['bio_helloworld'])

        super(Test, self).tearDown()
        redis_storage.delete_pattern('*')

        import shutil
        try:
            shutil.rmtree(self.repod)
        except FileNotFoundError:
            pass

    def test_reject(self):
        from biohub.core.plugins.user_plugin_manager import Repository

        class fakeuser:
            pass

        fakeuser.id = 1
        r = Repository(fakeuser)
        r.init('hsfzxjy', 'bio_helloworld').approve('23333')
        self.repod = r.repository_directory

        r = Repository(fakeuser)
        r.request_upgrade().reject('666')

    def test_drop(self):
        from biohub.core.plugins.user_plugin_manager import Repository

        class fakeuser:
            pass

        fakeuser.id = 1
        r = Repository(fakeuser)
        r.init('hsfzxjy', 'bio_helloworld').approve('23333')
        self.repod = r.repository_directory

        Repository(fakeuser).remove()

    def test_upgrade(self):
        from biohub.core.plugins.user_plugin_manager import Repository

        class fakeuser:
            pass

        fakeuser.id = 1
        r = Repository(fakeuser)
        r.init('hsfzxjy', 'bio_helloworld').approve('23333')
        self.repod = r.repository_directory

        r = Repository(fakeuser)
        r.request_upgrade().approve('666')

    def test_init(self):
        from biohub.core.plugins.user_plugin_manager import Repository, get_requests

        class fakeuser:
            pass

        fakeuser.id = 1

        r = Repository(fakeuser)
        req = r.init('hsfzxjy', 'bio_helloworld')
        self.assertEqual(len(get_requests()), 1)
        req.approve('23333')
        self.assertEqual(len(get_requests()), 0)
        self.repod = r.repository_directory

        r = Repository(fakeuser)
