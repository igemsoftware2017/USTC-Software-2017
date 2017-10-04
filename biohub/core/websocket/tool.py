import json
from functools import wraps

from channels import Group

from . import parsers


def get_group(name):
    """
    A shortcut to get and cache a Group object.
    """
    return Group(name)


def group_send(handler_name, group_name, data):
    """
    To send message to a specific group.
    """
    return get_group(group_name).send({
        'text': json.dumps(parsers.encode(handler_name, data))
    })


def broadcast(handler_name, data):
    """
    To make a global broadcasting.
    """
    return group_send(handler_name, 'broadcast', data)


def broadcast_user(handler_name, user, data):
    """
    To broadcast to specified user.
    """
    if isinstance(user, (int, str)):
        id = str(user)
    else:
        id = user.id
    return group_send(handler_name, 'user_%s' % id, data)


def broadcast_users(handler_name, users, data):
    """
    To broadcast to specified users.
    """
    return [
        broadcast_user(handler_name, user, data)
        for user in users
    ]


BROADCAST_FUNCTION_NAMES = (
    'group_send', 'broadcast', 'broadcast_user', 'broadcast_users'
)


def _method_proxy(name):
    """
    Searches a function in the global scope with the given name and wraps it
    into a Broadcaster instance method.
    """

    target_function = globals()[name]

    @wraps(target_function)
    def _proxy(self, *args, **kwargs):
        return target_function(self.handler_name, *args, **kwargs)

    return _proxy


Broadcaster = type(
    'Broadcaster',
    (),
    dict(
        __init__=lambda self, name: setattr(self, 'handler_name', name),
        __doc__="A helper class to broadcast websocket message.",
        **{name: _method_proxy(name) for name in BROADCAST_FUNCTION_NAMES})
)
