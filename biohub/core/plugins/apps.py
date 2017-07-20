from django.apps import AppConfig


class PluginsConfig(AppConfig):

    label = 'biohub_plugins'
    name = 'biohub.core.plugins'

    def ready(self):
        from biohub.core.conf import settings as biohub_settings
        from .registry import manager

        manager.populate_plugins(biohub_settings.BIOHUB_PLUGINS)
