from channels.generic.websockets import JsonWebsocketConsumer

from .registry import websocket_handlers


class MainConsumer(JsonWebsocketConsumer):

    http_user = True

    strict_ordering = False

    def connection_groups(self, **kwargs):
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
