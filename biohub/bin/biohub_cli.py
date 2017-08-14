#!/usr/bin/env python

"""
Biohub Command-Line Tool.
"""

import sys
import os
import os.path
import argparse

import django
from django.utils.functional import cached_property
from django.core.management import find_commands, load_command_class
from django.core.management.base import BaseCommand

# Resolve the base directory of biohub
current_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
biohub_base_dir = os.path.join(current_dir, '..', '..')

# Ensure that biohub can be globally imported
try:
    import biohub  # noqa
except ModuleNotFoundError:
    sys.path.insert(0, biohub_base_dir)

# Ensure that Mysql-python is patched and ready
from biohub import compat  # noqa
from biohub.utils.path import modpath  # noqa


class ManagementUtility(object):

    commands_mapping = {
        'plugin': {
            'new': 'newplugin',
            'mkmigrations': 'mkpluginmigrations',
            'migrate': 'migrateplugin',
            'install': 'installplugin',
            'remove': 'removeplugin'
        }
    }

    BIOHUB_PLUGINS_MODULE = 'biohub.core.plugins'

    def setup(self):
        """
        Set up django environment.
        """
        os.environ['DJANGO_SETTINGS_MODULE'] = 'biohub.main.settings.dev'
        os.environ.setdefault(
            'BIOHUB_CONFIG_PATH',
            os.path.join(biohub_base_dir, 'config.json'))

        django.setup()

    @cached_property
    def available_commands(self):
        """
        Returns a dict mappinng command names to their applications.
        """

        # Built-in commands from `biohub.core.plugins`
        commands = {
            name: self.BIOHUB_PLUGINS_MODULE for name in
            find_commands(
                modpath('.'.join([self.BIOHUB_PLUGINS_MODULE, 'management'])),
            )
        }

        return commands

    def fetch_command(self, subcommand):
        """
        Tries to fetch the given subcommand. If it can't be found, prints a
        message with the appropriate command called from the command line
        (e.g. "biohub_cli").
        """

        # Check if the subcommand is available
        try:
            app_name = self.available_commands[subcommand]
        except KeyError:
            sys.stderr.write(
                "Unknown command: %r\nType '%s --help' for usage.\n"
                % (subcommand, self.prog_name))
            sys.exit(1)

        if isinstance(app_name, BaseCommand):
            klass = app_name
        else:
            klass = load_command_class(app_name, subcommand)

        return klass

    def execute(self):
        """
        The main function of the tool.
        """

        self.setup()

        self.argv = sys.argv[:]
        self.prog_name = os.path.basename(sys.argv[0])

        parser = argparse.ArgumentParser(
            prog=self.prog_name,
            usage='%(prog)s <command> [<args>]',
            description='Biohub CLI Tool')

        parser.add_argument(
            'command',
            choices=self.commands_mapping,
            help='Available commands: %s.' % ', '.join(self.commands_mapping)
        )

        # if no command provided
        if len(self.argv) < 2:
            parser.print_help()
            sys.exit()

        command = parser.parse_args(self.argv[1:2]).command

        getattr(self, command)()

    def plugin(self):
        """
        The main function of plugin command.
        """

        plugin_commands = self.commands_mapping['plugin']

        parser = argparse.ArgumentParser(
            prog=self.prog_name,
            usage='%(prog)s plugin <subcommand> [<args>]')

        parser.add_argument(
            'subcommand',
            choices=plugin_commands,
            help='Available subcommands: %s.' % ', '.join(plugin_commands))

        # if no subcommand provided
        if not self.argv[2:]:
            parser.print_help()
            sys.exit()

        subcommand = parser.parse_args(self.argv[2:3]).subcommand

        self.fetch_command(
            plugin_commands[subcommand]).run_from_argv(self.argv[1:])


if __name__ == '__main__':
    ManagementUtility().execute()
