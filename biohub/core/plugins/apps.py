from django.apps import AppConfig


class PluginsConfig(AppConfig):

    label = 'biohub_plugins'
    name = 'biohub.core.plugins'

    def ready(self):
        from biohub.core.plugins import plugins

        plugins.populate_plugins()
