from django.apps import apps
from django.core.management import BaseCommand, call_command

from biohub.core.plugins import install


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'plugin',
            help='mod_path of the plugin')

    def handle(self, plugin, **options):
        install([plugin])

        for app_config in apps.app_configs.values():

            if app_config.name == plugin:
                call_command('makemigrations', app_config.label)
