from . import parsers


class MessageWrapper(object):
    """
    To provide a more easy-use interface for websocket handler writers.
    """

    def __init__(self, consumer, content):
        self.handler_name, self.data = parsers.decode(content)
        self.user = consumer.message.user
        self.__consumer = consumer

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

    def broadcast(self, data):
        """
        To make a global broadcast.
        """
        self.group_send('broadcast', data)

    def broadcast_user(self, user, data):
        """
        To broadcast to a specified user.
        """
        self.group_send('user_%s' % user.id, data)

    def broadcast_users(self, users, data):
        """
        To broadcast to a group a users.
        """
        for user in users:
            self.broadcast_user(user, data)
