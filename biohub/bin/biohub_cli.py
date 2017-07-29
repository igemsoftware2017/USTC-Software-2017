#!/usr/bin/env python

"""
Biohub Command-Line Tool.
"""

import sys
import os
import os.path
from collections import defaultdict

import django
from django.utils.functional import cached_property
from django.core.management import find_commands, load_command_class
from django.core.management.color import color_style
from django.core.management.base import (
    CommandParser, BaseCommand)

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
    """
    Encapsulates the logic of this CLI tool.
    """

    BIOHUB_PLUGINS_MODULE = 'biohub.core.plugins'

    def __init__(self):

        self.argv = sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])

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

    def setup(self):
        """
        Sets up essential environment variables, and configures django.
        """
        os.environ['DJANGO_SETTINGS_MODULE'] = 'biohub.main.settings.dev'
        os.environ.setdefault(
            'BIOHUB_CONFIG_PATH',
            os.path.join(biohub_base_dir, 'config.json'))

        django.setup()

    def main_help_text(self, commands_only=False):
        """
        Returns the script's main help text, as a string.

        By setting `commands_only` to True, the function will just return
        the names of available commands, separated by new lines.
        """

        if commands_only:
            usage = sorted(self.available_commands.keys())
        else:
            usage = [
                "",
                "Type '%s help <subcommand>' for help on a specific"
                " subcommand." % self.prog_name,
                "",
                "Available subcommands:"]

            # Gather up available commands
            commands_dict = defaultdict(list)
            for name, app in self.available_commands.items():

                if app == self.BIOHUB_PLUGINS_MODULE:
                    app = 'biohub.plugins'
                else:
                    app = app.rpartition('.')[-1]

                commands_dict[app].append(name)

            style = color_style()

            # Construct help text
            for app in sorted(commands_dict.keys()):
                usage.append("")
                usage.append(style.NOTICE("[%s]" % app))  # title
                for name in sorted(commands_dict[app]):
                    usage.append("    %s" % name)

        return '\n'.join(usage)

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
                "Unknown command: %r\nType '%s help' for usage.\n"
                % (subcommand, self.prog_name))
            sys.exit(1)

        if isinstance(app_name, BaseCommand):
            klass = app_name
        else:
            klass = load_command_class(app_name, subcommand)

        return klass

    def execute(self):
        """
        Given the command-line arguments, the function figures out which
        subcommand to be executed, creates a parser appropriate to that
        command, and runs it.
        """
        self.setup()

        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = 'help'  # Display help if no arguments were given

        # Preprocess options
        parser = CommandParser(
            None,
            usage='%(prog)s subcommand [options] [args]', add_help=False)
        parser.add_argument('args', nargs='*')
        # Capture all remaining arguments
        options, args = parser.parse_known_args(self.argv[2:])

        if subcommand == 'help':
            if '--commands' in args:
                sys.stdout.write(
                    self.main_help_text(commands_only=True) + '\n')
            elif len(options.args) < 1:
                sys.stdout.write(self.main_help_text() + '\n')
            else:
                self.fetch_command(options.args[0])\
                    .print_help(self.prog_name, options.args[0])
        elif self.argv[1:] in (['--help'], ['-h']):
            sys.stdout.write(self.main_help_text() + '\n')
        else:
            self.fetch_command(subcommand).run_from_argv(self.argv)


if __name__ == '__main__':
    ManagementUtility().execute()
