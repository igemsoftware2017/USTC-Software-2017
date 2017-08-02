from biohub.utils.registry.base import SignalRegistryBase
from biohub.core.websocket.message import MessageWrapper

SPECIAL_HANDLER_NAMES = ('__connect__', '__disconnect__')


class WebsocketHandlerRegistry(SignalRegistryBase):

    submodules_to_populate = ('ws_handlers', )
    providing_args = ('message',)

    def dispatch(self, consumer, content=None):
        message = MessageWrapper(consumer, content)

        if message.handler_name == '__error__':
            message.reply(message.packed_data)
            return

        handler_name = message.handler_name
        if handler_name not in self.signal_mapping:
            return

        super(WebsocketHandlerRegistry, self).dispatch(
            handler_name, message=message)


websocket_handlers = WebsocketHandlerRegistry()

register, unregister, cache_clear = map(
    lambda field_name: getattr(websocket_handlers, field_name),
    ('register_decorator', 'unregister', 'cache_clear'))

register_connected, register_disconnected = map(
    register, SPECIAL_HANDLER_NAMES)
