from django.core.management import call_command

from ._base import PluginCommand


class Command(PluginCommand):

    help = 'Creates new migration(s) for plugins.'

    def handle(self, plugin, **options):
        super(Command, self).handle(plugin, **options)

        call_command('makemigrations', self.plugin_config.label)
