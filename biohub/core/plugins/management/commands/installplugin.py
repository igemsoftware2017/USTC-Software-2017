from ._base import PluginCommand

from biohub.core.conf import dump_config


class Command(PluginCommand):

    help = "Add a new plugin to configuration file."

    def handle(self, plugin, **options):
        super(Command, self).handle(plugin, **options)

        dump_config()
