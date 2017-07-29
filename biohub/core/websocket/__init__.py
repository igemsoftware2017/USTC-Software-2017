from .registry import websocket_handlers

register_handler = websocket_handlers.register_decorator
unregister_handler = websocket_handlers.unregister
