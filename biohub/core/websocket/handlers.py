from .signals import ws_received

from functools import wraps


class register_handler(object):
    """
    A decorator for websocket handler registration.
    """
    def __init__(self, handler_name, uid=None):
        self._handler_name = handler_name
        self._uid = uid

    def __call__(self, func):

        @wraps(func)
        def _inner(sender, message, **kwargs):
            if message.handler_name != self._handler_name:
                return
            func(message)

        ws_received.connect(_inner, dispatch_uid=self._uid)

        _inner.handler_name = self._handler_name

        return _inner


def unregister_handler(receiver, uid=None):
    """
    A function to unregister a handler.
    """
    ws_received.disconnect(
        receiver,
        dispatch_uid=uid
    )
