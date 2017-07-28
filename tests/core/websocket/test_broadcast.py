from biohub.core.websocket.tool import broadcast, broadcast_user

from ._base import WSTestCase


class Test(WSTestCase):

    def test_broadcast_user(self):
        data = dict(msg='test')
        broadcast_user(self.user1, data)

        self.assertEqual(data, self.client1.receive())
        self.assertIsNone(self.client2.receive())

    def test_broadcast(self):

        client1 = self.client1
        client2 = self.client2

        data = dict(msg='test')

        broadcast(data)

        self.assertEqual(client1.receive(), data)
        self.assertEqual(client2.receive(), data)
