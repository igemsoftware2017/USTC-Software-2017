from os import path

from django.apps import apps
from django.core.management import BaseCommand, CommandError

from biohub.utils import module as module_util, path as path_util
from biohub.core.plugins import install


class PluginCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'plugin',
            help='Dotted path or directory of the plugin.')

    def fail_installation(self):
        raise CommandError("Plugin '%s' cannot be properly installed."
                           % self.plugin_name)

    def handle_plugin_name(self, value):

        if not value:
            raise CommandError(
                "You should specify the dotted path or directory "
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

    def handle(self, plugin, *args, **kwargs):
        self.plugin_name = self.handle_plugin_name(plugin)
        plugin_name = self.plugin_name

        if not install([plugin_name], invalidate_urlconf=False):
            self.fail_installation()

        try:
            self.plugin_config = [
                ac for ac in apps.app_configs.values()
                if ac.name == plugin_name][0]
        except IndexError:
            self.fail_installation()
