from ._base import PluginCommand, CommandError

from biohub.core.conf import manager as settings_manager


class Command(PluginCommand):

    help = "Add a new plugin to configuration file."

    def handle(self, plugin, **options):

        try:
            super(Command, self).handle(plugin, **options)
        except CommandError:
            pass

        settings_manager.dump()
