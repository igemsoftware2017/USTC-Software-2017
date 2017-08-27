from channels.test import ChannelTestCase, WSClient


class BiohubWSClient(WSClient):
    """
    A more convenient websocket client for testing.
    """

    def send_content(self, data, path='/ws/', *args, **kwargs):

        return self.send_and_consume(
            'websocket.receive', text=data, path=path, *args, **kwargs)

    def connect(self, path='/ws/'):
        return self.send_and_consume('websocket.connect', path=path)

    def disconnect(self, path='/ws/'):
        return self.send_and_consume('websocket.disconnect', path=path)

    @classmethod
    def from_user(cls, user):
        instance = cls()
        instance.force_login(user)
        return instance


class WSTestCase(ChannelTestCase):
    """
    A more convenient test case to test websocket.
    """

    client_class = BiohubWSClient

    def receive(self):
        """
        A shortcut to `client.receive`.
        """
        return self.client.receive()

    def send_content(self, *args, **kwargs):
        """
        A shortcut to `client.send_content`.
        """
        return self.client.send_content(*args, **kwargs)

    def connect(self, *args, **kwargs):
        """
        A shortcut to `client.connect`.
        """
        return self.client.connect(*args, **kwargs)

    def disconnect(self, *args, **kwargs):
        """
        A shortcut to `client.disconnect`.
        """
        return self.client.disconnect(*args, **kwargs)

    def new_client(self, user=None):
        """
        A factory function to create new WSClient.

        If argument `user` is supplied, it will be logined with the client
        right after the client was created.
        """
        client = self.client_class()

        if user is not None:
            client.force_login(user)

        return client
