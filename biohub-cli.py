#!/usr/bin/env python3

"""
Biohub Command-Line Tool.
"""

import sys
import os
import os.path
import argparse

import django
from django.utils.functional import cached_property
from django.core.management import find_commands, load_command_class, call_command
from django.core.management.base import BaseCommand

# Resolve the base directory of biohub
current_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
biohub_base_dir = current_dir

# Ensure that biohub can be globally imported
try:
    import biohub  # noqa
except ModuleNotFoundError:
    sys.path.insert(0, biohub_base_dir)

# Ensure that Mysql-python is patched and ready
from biohub import compat  # noqa
from biohub.utils.path import modpath  # noqa


def resolve(*paths):
    return os.path.join(biohub_base_dir, *paths)


class ManagementUtility(object):

    commands_mapping = {
        'plugin': {
            'new': 'newplugin',
            'mkmigrations': 'mkpluginmigrations',
            'migrate': 'migrateplugin',
            'install': 'installplugin',
            'remove': 'removeplugin'
        },
        'init': {

        },
        'installjob': {

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
            resolve('config.json')
        )

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

    def fetch_command(self, subcommand, command_sets=None):
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

    def installjob(self):
        from biohub.biobrick.management.commands.installjob import Command
        Command().run_from_argv(self.argv[:])

    def _run_cmd(self, commands, output, input=sys.stdin):

        from subprocess import Popen, PIPE

        p = Popen(
            commands,
            stdout=sys.stdout if output else PIPE,
            stderr=sys.stderr if output else PIPE,
            stdin=input
        )
        p.communicate()
        return p.returncode

    def _detect(self, name, commands):

        print('Detecting {}...'.format(name))
        if self._run_cmd(commands, True) != 0:
            print('{} not detected.'.format(name))
            sys.exit(1)
        else:
            print('{} detected.\n'.format(name))

    def _run_mysql(self, *commands, input=None, output=True):
        return self._run_cmd([
            'mysql',
            '-u%s' % self.db_user,
            ('-p%s' % self.db_password if self.db_password else ''),
            '-h%s' % self.db_host,
            '-P%s' % self.db_port,
            *commands
        ], output, input=input)

    def _run_mysql_cmd(self, command):
        return self._run_mysql(
            '-e',
            command
        )

    def _prepare_db(self):

        from biohub.core.conf import settings
        db_config = settings.DEFAULT_DATABASE

        self.db_name = db_config['NAME']
        self.db_user = db_config['USER']
        self.db_password = db_config['PASSWORD']
        self.db_host = db_config['HOST']
        self.db_port = db_config['PORT']

        self._prepare_igem()

        if self._run_mysql_cmd('USE %s;' % self.db_name):
            print('Creating main database...')
            self._run_mysql_cmd('CREATE DATABASE %s CHARACTER SET utf8;' % self.db_name)

        call_command('migrate')
        print('\nMain database prepared.')

    def _prepare_igem(self):

        import errno
        try:
            os.makedirs(resolve('_download'))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        dest = resolve('_download', 'biobricks.sql')

        if not os.path.isfile(dest):
            gz_dest = resolve('_download', 'biobricks.sql.gz')
            if os.path.isfile(gz_dest):
                print('Download cache detected.')
            else:
                from biohub.utils.download import download
                download('http://parts.igem.org/partsdb/download.cgi?type=parts_sql', dest=gz_dest)[0].close()

                print('Extracting...')
                self._run_cmd(['gunzip', gz_dest, '-k', '-f'], True)

        print('Importing initial data...')
        self._run_mysql_cmd('CREATE DATABASE IF NOT EXISTS igem CHARACTER SET utf8;')
        self._run_mysql('igem', input=open(dest, 'r'))
        print('Initial data imported.\n')
        print('Preprocessing initial data...')
        self._run_cmd([
            sys.executable,
            resolve('biohub', 'biobrick', 'bin', 'updateparts.py'),
            '--host', self.db_host,
            '--port', self.db_port,
            '--user', self.db_user,
            *(['--password', self.db_password] if self.db_password else []),
            '--chunk', '500'
        ], True)

    def _prepare_weights(self):

        print('\nCalculating weights for the first time...')
        call_command('refreshweight', update_index=True, age='15s')

    def _prepare_graph(self):
        print('\nInstalling relationships of bricks...')
        call_command('installgraph')
        print('Relationships installed.\n')

    def init(self):
        """
        The main function of init command.
        """

        self._detect('mysql', ['mysql', '--version'])
        self._detect('redis', ['redis-cli', '--version'])

        self._prepare_db()
        self._prepare_graph()
        self._prepare_weights()

        print('\nCompiling biocircuit...')
        self._run_cmd(['/usr/bin/python3', resolve('biohub', 'biocircuit', 'compile-espresso.py')], True)
        print('Compiled.\n')
        print('Finished initialization.')


if __name__ == '__main__':
    if sys.version_info[0] < 3 or sys.version_info[1] < 5:
        print('Your python version is too low.')
        sys.exit(1)
    ManagementUtility().execute()
