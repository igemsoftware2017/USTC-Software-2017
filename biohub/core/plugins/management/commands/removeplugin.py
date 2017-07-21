from biohub.core.plugins import manager as plugins_manager

from ._base import PluginCommand


class Command(PluginCommand):

    help = "Remove a plugin from the configuration file."

    def handle(self, plugin, **options):

        plugin_name = self.handle_plugin_name(plugin)

        plugins_manager.remove([plugin_name], update_config=True)
