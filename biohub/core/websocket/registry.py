from biohub.utils.registry.base import SignalRegistryBase
from biohub.core.websocket.message import MessageWrapper

SPECIAL_HANDLER_NAMES = ('__connect__', '__disconnect__')


class WebsocketHandlerRegistry(SignalRegistryBase):
    """
    A manager class to provide message dispatching, handlers
    registration/unregistration utilities.
    """

    submodules_to_populate = ('ws_handlers', )
    providing_args = ('message',)

    def dispatch(self, consumer, content=None):
        """
        Given a consumer and optional incoming content, the function packs
        essential information into a MessageWrapper object, and dispatches
        it to handlers specified by `handler_name` in the content.
        """

        message = MessageWrapper(consumer, content)

        # Returns directly if error occurs while parsing incoming data
        if message.handler_name == '__error__':
            message.reply(message.packed_data)
            return

        handler_name = message.handler_name
        # Silently returns if no corresponding handlers found
        if handler_name not in self.signal_mapping:
            return

        super(WebsocketHandlerRegistry, self).dispatch(
            handler_name, message=message)


websocket_handlers = WebsocketHandlerRegistry()

# Shorthand functions
register, unregister, cache_clear = map(
    lambda field_name: getattr(websocket_handlers, field_name),
    ('register_decorator', 'unregister', 'cache_clear'))

register_connected, register_disconnected = map(
    register, SPECIAL_HANDLER_NAMES)
