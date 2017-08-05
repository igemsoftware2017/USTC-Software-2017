from biohub.core.websocket.test import WSTestCase
from biohub.accounts.models import User


class Test(WSTestCase):

    def setUp(self):
        self.me = User.objects.create_test_user('me')

    def test_connect_fail(self):
        with self.assertRaises(AssertionError):
            self.connect()

    def test_connect_success(self):
        self.client.force_login(self.me)
        self.connect()
        self.disconnect()
