from biohub.core.websocket.tool import broadcast, broadcast_user, \
    broadcast_users

from ._base import WSTestCase


class Test(WSTestCase):

    def test_broadcast_user(self):
        data = dict(msg='test')
        broadcast_user('test', self.user1, data)

        self.assertEqual(data, self.client1.receive()['data'])
        self.assertIsNone(self.client2.receive())

    def test_broadcast_users(self):
        data = dict(msg='test')
        broadcast_users('test', [self.user1, self.user2], data)

        self.assertEqual(data, self.client1.receive()['data'])
        self.assertEqual(self.client2.receive()['data'], data)

    def test_broadcast(self):

        client1 = self.client1
        client2 = self.client2

        data = dict(msg='test')

        broadcast('test', data)

        self.assertEqual(client1.receive()['data'], data)
        self.assertEqual(client2.receive()['data'], data)
