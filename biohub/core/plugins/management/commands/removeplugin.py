from biohub.core.plugins import plugins

from ._base import PluginCommand


class Command(PluginCommand):

    help = "Remove a plugin from the configuration file."

    def handle(self, plugin, **options):

        plugin_name = self.handle_plugin_name(plugin)

        plugins.remove([plugin_name], update_config=True)
