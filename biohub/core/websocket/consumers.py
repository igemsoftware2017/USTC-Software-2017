from channels.generic.websockets import JsonWebsocketConsumer
from . import signals
from .message import MessageWrapper
from .parsers import WebSocketDataDecodeError


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
        self.message.reply_channel.send({
            "accept": self.message.user.is_authenticated()
        })

    def receive(self, content, **kwargs):
        """
        Dispatches incoming content to corresponding handlers.
        """
        try:
            message = MessageWrapper(self, content)
        except WebSocketDataDecodeError as e:
            self.send(dict(handler='__error__', data=str(e)))
        else:
            signals.ws_received.send(self.__class__, message=message)
