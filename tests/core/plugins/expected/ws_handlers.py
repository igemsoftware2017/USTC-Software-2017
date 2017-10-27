from biohub.core.websocket import register_handler, register_connected  # noqa

# Place your websocket handlers here.
#
# Example:
#
# @register_handler('my_plugin')
# def handler(message):
#     # Simple echo back the data
#     message.reply(message.data)
#
# @register_connected
# def connected(message):
#     with message.patch_handler_name('my_plugin'):
#         # the message will be sent every time a new connection established
#         message.reply('connected to my_plugin')
