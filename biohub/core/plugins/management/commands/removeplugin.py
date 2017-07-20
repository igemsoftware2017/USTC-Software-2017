from ._base import PluginCommand
from biohub.core import conf


class Command(PluginCommand):

    help = "Remove a plugin from the configuration file."

    def handle(self, plugin, **options):

        plugin_name = self.handle_plugin_name(plugin)

        try:
            conf.settings.BIOHUB_PLUGINS.remove(plugin_name)
        except ValueError:
            pass

        conf.manager.dump()
