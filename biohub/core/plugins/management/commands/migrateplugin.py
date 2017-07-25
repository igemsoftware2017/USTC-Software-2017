import os
from django.core.management import call_command

from biohub.utils.db import patch_test_db

from ._base import PluginCommand


class Command(PluginCommand):

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        parser.add_argument(
            'migration_name',
            nargs='?',
            help='Database state will be brought to the state after that'
            ' migration. Use the name "zero" to unapply all migrations.')
        parser.add_argument(
            '--no-output',
            dest='no_output',
            default=False,
            action='store_true',
            help='Trap the output content when applying migrations.')
        parser.add_argument(
            '--test',
            dest='test',
            default=False,
            action='store_true',
            help='Switch database configuration for testing.')
        parser.add_argument(
            '--no-input',
            action='store_false',
            dest='interactive',
            default=True,
            help='Tells Django to NOT prompt the user for input of any kind.')

    def handle(self, plugin, migration_name, **options):

        super(Command, self).handle(plugin, migration_name, **options)

        plugin_config = self.plugin_config

        with patch_test_db(options['test']):

            stdout = open(os.devnull, 'w', encoding='utf-8') \
                if options['no_output'] else self.stdout

            call_command(
                'migrate', plugin_config.label, migration_name=migration_name,
                verbosity=options['verbosity'], stdout=stdout,
                interactive=options['interactive'])

            if stdout is not self.stdout:
                stdout.close()
