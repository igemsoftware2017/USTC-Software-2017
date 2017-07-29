from biohub.core.websocket.consumers import MainConsumer

channels_routing = [
    MainConsumer.as_route(path=r'^/ws/')
]
