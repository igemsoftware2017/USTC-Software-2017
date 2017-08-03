from channels.generic.websockets import JsonWebsocketConsumer

from .registry import websocket_handlers


class MainConsumer(JsonWebsocketConsumer):

    http_user = True

    strict_ordering = False

    def connection_groups(self, **kwargs):
        """
        Each connection belongs to 2 groups: broadcast and user_<userid>.
        The first one is for global broadcasting and the second one is for
        user specific broadcasting.
        """

        groups = ['broadcast']
        if self.message.user.is_authenticated():
            groups.append('user_%s' % self.message.user.id)

        return groups

    def connect(self, message, **kwargs):
        """
        Rejects if user is not authenticated.
        """

        accept = self.message.user.is_authenticated()

        self.message.reply_channel.send({
            "accept": accept
        })

        if accept:
            websocket_handlers.dispatch(self, {
                'handler': '__connect__',
                'data': ''
            })

    def receive(self, content, **kwargs):
        """
        Dispatches incoming content to corresponding handlers.
        """
        websocket_handlers.dispatch(self)
