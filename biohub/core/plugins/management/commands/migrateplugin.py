import os
from os import path

from django.apps import apps
from django.core.management import BaseCommand, call_command, CommandError

from biohub.core.plugins import install
from biohub.utils.db import patch_test_db
from biohub.utils import path as path_util, module as module_util


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'plugin_mod_path',
            help='Dot-separated python module path or directory of the plugin.')
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

    def fail_installation(self):
        raise CommandError("Plugin '%s' cannot be properly installed."
                           % self.plugin_mod_path)

    def handle_mod_path(self, value):

        if not value:
            raise CommandError("You should specify the mod_path or directory "
                               "of the plugin.")

        # Try as a dot-separated python module path.
        valid_mod_path = module_util.is_valid_module_path(value, True)

        # Try as a directory
        valid_dir = False
        directory = path_util.realdir(value)
        init_file_path = path.join(directory, '__init__.py')
        valid_dir = path.isdir(directory) and path.isfile(init_file_path)

        if valid_dir:
            module = module_util.module_from_file_location(init_file_path)
            mod_path = module.default_app_config.rsplit('.', 2)[0]

        # Analyze the result
        if valid_mod_path and valid_dir:
            raise CommandError("The mod_path '%s' is ambigious. " % value)
        elif valid_mod_path:
            return value
        elif valid_dir:
            return mod_path
        else:
            raise CommandError(
                "The mod_path '%s' is neither a "
                "dot-separated module path nor a directory." % value)

    def handle(self, plugin_mod_path, migration_name, **options):

        self.plugin_mod_path = self.handle_mod_path(plugin_mod_path)
        plugin_mod_path = self.plugin_mod_path

        # Fail if unsuccessfully installed
        if not install([plugin_mod_path]):
            self.fail_installation()

        with patch_test_db(options['test']):

            # Get the app_label of the plugin
            try:
                label = [
                    app_config for app_config in apps.app_configs.values()
                    if app_config.name == plugin_mod_path][0].label
            except IndexError:
                self.fail_installation()

            stdout = open(os.devnull, 'w', encoding='utf-8') \
                if options['no_output'] else self.stdout

            call_command(
                'migrate', label, migration_name=migration_name,
                verbosity=options['verbosity'], stdout=stdout,
                interactive=options['interactive'])

            if stdout is not self.stdout:
                stdout.close()
