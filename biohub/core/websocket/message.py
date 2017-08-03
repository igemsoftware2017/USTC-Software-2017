import json

from . import parsers, tool


class MessageWrapper(object):
    """
    To provide a more easy-use interface for websocket handler writers.
    """

    def __init__(self, consumer, content=None):
        if content is None:
            content = json.loads(consumer.message.content['text'])

        try:
            self.handler_name, self.data = parsers.decode(content)
        except parsers.WebsocketDataDecodeError as e:
            self.handler_name, self.data = '__error__', str(e)

        self.user = consumer.message.user
        self.__consumer = consumer
        self.__broadcaster = tool.Broadcaster(self.handler_name)

    @property
    def packed_data(self):
        return parsers.encode(self.handler_name, self.data)

    def reply(self, data):
        """
        A shortcut for replying.
        """
        wrapped = parsers.encode(self.handler_name, data)

        self.__consumer.send(wrapped)

    def group_send(self, group_name, data):
        """
        A shortcut for group message sending.
        """
        wrapped = parsers.encode(self.handler_name, data)

        self.__consumer.group_send(group_name, wrapped)

    def __getattribute__(self, name):
        if name in tool.BROADCAST_FUNCTION_NAMES:
            return getattr(self.__broadcaster, name)

        return object.__getattribute__(self, name)

    @contextlib.contextmanager
    def patch_handler_name(self, handler_name):
        """
        A context manager to provide convenience for temporary handler name
        modification.
        """

        old = self.handler_name

        self.handler_name = self.__broadcaster.handler_name = handler_name
        yield
        self.handler_name = self.__broadcaster.handler_name = old
