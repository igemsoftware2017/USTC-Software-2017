from .registry import (  # noqa
    websocket_handlers, register_connected, register_disconnected
)

register_handler = websocket_handlers.register_decorator
unregister_handler = websocket_handlers.unregister
