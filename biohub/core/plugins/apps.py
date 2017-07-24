from django.apps import AppConfig


class PluginsConfig(AppConfig):

    label = 'biohub_plugins'
    name = 'biohub.core.plugins'

    def ready(self):
        from .registry import manager

        manager.populate_plugins()
