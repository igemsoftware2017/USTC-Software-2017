from tests.core.websocket._base import WSTestCase

from biohub.notices import tool


class Test(WSTestCase):

    def test_connected(self):
        self.recover_ws_patching()

        client = self.new_client(self.user1)
        tool.Dispatcher('a').send(self.user1, 'hello')
        client.connect()

        self.assertEqual(client.receive(), {
            'handler': 'notices',
            'data': 1
        })

    def test_fetch(self):
        self.recover_ws_patching()

        client = self.new_client(self.user1)
        client.connect()
        tool.Dispatcher('a').send(self.user1, 'hello')
        client.send_content(dict(handler='notices', data='fetch'))

        self.assertEqual(client.receive(), {
            'handler': 'notices',
            'data': 0
        })

        self.assertEqual(client.receive(), {
            'handler': 'notices',
            'data': 1
        })
