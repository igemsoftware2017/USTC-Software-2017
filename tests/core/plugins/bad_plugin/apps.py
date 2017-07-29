from biohub.core.plugins import PluginConfig


class BadPluginConfig(PluginConfig):

    name = 'tests.core.plugins.bad_plugin'
    title = 'My Plugin'
    author = 'hsfzxjy'
    description = 'This is my plugin.'

    def ready(self):
        raise ZeroDivisionError
