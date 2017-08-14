from channels.routing import route

from biohub.core.websocket.consumers import MainConsumer
from biohub.core.tasks.consumers import task_consumer

channels_routing = [
    MainConsumer.as_route(path=r'^/ws/'),
    route('task', task_consumer)
]
