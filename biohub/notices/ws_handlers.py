from biohub.core.websocket import register_connected, register_handler

from .models import Notice


def echo_notices_stats(message):
    message.reply(
        list(Notice.objects
             .user_notices(message.user).stats())
    )


@register_handler('notices')
def notices_handler(message):
    if message.data == 'fetch':
        echo_notices_stats(message)


@register_connected
def ws_connected(message):
    """
    Echos stats of user notices every time a connection established.
    """

    with message.patch_handler_name('notices'):
        echo_notices_stats(message)
