from django.apps import AppConfig


class CoreConfig(AppConfig):

    name = 'biohub.core'
    label = 'biohub_core'

    def ready(self):
        from biohub.core.conf.signal import register
        from biohub.core.plugins.ipc_slave import bridge

        bridge.register()
        register()
