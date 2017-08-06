from biohub.core.websocket import test
from biohub.core.websocket.registry import websocket_handlers
from biohub.accounts.models import User


class WSTestCase(test.WSTestCase):

    def tearDown(self):
        self.recover_ws_patching()

    def recover_ws_patching(self):
        websocket_handlers.signal_mapping = self._old_mapping

    def setUp(self):

        # Mock
        self._old_mapping = websocket_handlers.signal_mapping
        websocket_handlers.signal_mapping = {}

        self.user1 = user1 = User.objects.create_user(
            username='user1', password='user1')
        self.user2 = user2 = User.objects.create_user(
            username='user2', password='user2')

        self.client1 = self.new_client(user1)
        self.client2 = self.new_client(user2)

        self.client1.connect()
        self.client2.connect()
