import django.dispatch

ws_received = django.dispatch.Signal(providing_args=['message'])
