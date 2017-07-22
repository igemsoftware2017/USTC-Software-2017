from ._base import PluginCommand

from biohub.core.conf import manager as settings_manager


class Command(PluginCommand):

    help = "Add a new plugin to configuration file."

    def handle(self, plugin, **options):
        super(Command, self).handle(plugin, **options)

        settings_manager.dump()
