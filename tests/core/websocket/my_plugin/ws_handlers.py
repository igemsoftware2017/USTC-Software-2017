from biohub.core.websocket import register_handler


@register_handler('my_plugin')
def handle(message):
    message.reply('my_plugin')
