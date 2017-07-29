from biohub.utils.registry.base import DictRegistryBase

from biohub.core.websocket.message import MessageWrapper


class WebsocketHandlerRegistry(DictRegistryBase):

    submodules_to_populate = ('ws_handlers', )

    def dispatch(self, consumer):
        message = MessageWrapper(consumer)

        if message.handler_name == '__error__':
            message.reply(message.packed_data)
            return

        handler_name = message.handler_name
        if handler_name not in self.mapping:
            return

        handler = self.mapping[handler_name]
        handler(message)


websocket_handlers = WebsocketHandlerRegistry()

register, unregister, cache_clear = map(
    lambda field_name: getattr(websocket_handlers, field_name),
    ('register_decorator', 'unregister', 'cache_clear'))
