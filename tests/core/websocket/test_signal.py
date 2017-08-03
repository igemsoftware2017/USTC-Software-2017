from biohub.core.plugins import install, plugins, remove

from ._base import WSTestCase


class Test(WSTestCase):

    def setUp(self):
        super(Test, self).setUp()
        self._protect = plugins.protect(test=True)
        self._protect.acquire()

    def tearDown(self):
        self._protect.release()

    def test_dup_connected(self):
        from biohub.core.websocket import register_connected, unregister_handler  # noqa
        func = lambda m: m.reply(m.user.id)  # noqa
        _ = register_connected(func)  # noqa

        with self.assertRaises(KeyError):
            __ = register_connected(func)  # noqa

        unregister_handler(_)

    def test_connected(self):
        from biohub.core.websocket import register_connected, unregister_handler  # noqa

        _ = register_connected(lambda m: m.reply(m.user.id))  # noqa
        __ = register_connected(lambda m: m.reply('hi'))  # noqa

        client = self.new_client(self.user1)
        client.connect()

        self.assertEqual(client.receive()['data'], self.user1.id)
        self.assertEqual(client.receive()['data'], 'hi')

        unregister_handler(_)
        unregister_handler(__)

        client = self.new_client(self.user1)
        client.connect()

        self.assertIsNone(client.receive())

    def test_unregister(self):

        from biohub.core.websocket import register_handler, unregister_handler
        _ = register_handler('test')(lambda m: m.reply(m.data))  # noqa
        unregister_handler(_)

        data = {
            'handler': 'test',
            'data': 'helloworld'
        }

        self.client1.send_content(data)
        self.assertIsNone(self.client1.receive())

    def test_signal(self):
        from biohub.core.websocket import register_handler, unregister_handler
        _ = register_handler('test')(lambda m: m.reply(m.data))  # noqa

        data = {
            'handler': 'test',
            'data': 'helloworld'
        }

        self.client1.send_content(data)
        self.assertEqual(self.client1.receive(), data)
        self.assertIsNone(self.client2.receive())

        unregister_handler(_)
        self.client1.send_content(data)
        self.assertIsNone(self.client1.receive())

    def test_plugin(self):

        name = 'tests.core.websocket.my_plugin'
        install([name])
        plugins.populate_plugins()

        self.client1.send_content({
            'handler': 'my_plugin',
            'data': ''
        })
        self.assertEqual(self.client1.receive()['data'], 'my_plugin')
        self.assertIsNone(self.client1.receive())

        remove([name])
        self.client1.send_content({
            'handler': 'my_plugin',
            'data': ''
        })
        self.assertIsNone(self.client1.receive())

    def test_user(self):
        from biohub.core.websocket import register_handler
        _ = register_handler('test')(lambda m: m.reply(m.user.id))  # noqa

        self.client1.send_content(dict(handler='test', data=''))
        self.assertEqual(self.user1.id, self.client1.receive()['data'])

        del _

    def test_error(self):
        self.client1.send_content({1: 2})

        self.assertDictContainsSubset({
            'handler': '__error__',
        }, self.client1.receive())

    def test_broadcast(self):
        from biohub.core.websocket import register_handler
        _ = register_handler('test')(lambda m: m.broadcast('hi'))  # noqa

        self.client1.send_content(dict(handler='test', data=''))
        self.assertEqual(self.client1.receive()['data'], 'hi')
        self.assertEqual(self.client2.receive()['data'], 'hi')

    def test_broadcast_user(self):
        from biohub.core.websocket import register_handler
        _ = register_handler('test')(  # noqa
            lambda m: m.broadcast_user(self.user2, 'hi'))  # noqa

        self.client1.send_content(dict(handler='test', data=''))
        self.assertIsNone(self.client1.receive())
        self.assertEqual(self.client2.receive()['data'], 'hi')

    def test_broadcast_users(self):
        from biohub.core.websocket import register_handler
        _ = register_handler('test')(  # noqa
            lambda m: m.broadcast_users([self.user1, self.user2], 'hi'))  # noqa

        self.client1.send_content(dict(handler='test', data=''))
        self.assertEqual(self.client1.receive()['data'], 'hi')
        self.assertEqual(self.client2.receive()['data'], 'hi')
