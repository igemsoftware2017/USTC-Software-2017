import os
import io
import importlib
import shutil
import errno
from os import path

import django
from django.template import Context, Engine
from django.conf import settings
from django.core.management import CommandError, BaseCommand

from biohub.utils.path import modpath


class Command(BaseCommand):

    rewrite_template_suffixes = (
        # Allow shipping invalid .py files without byte-compilation.
        ('.py-tpl', '.py'),
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'name',
            help='Name of the new plugin.')
        parser.add_argument(
            'mod_path',
            help='Dot-separated python module path referring to the '
            'plugin. NOTE THAT the path should be globally visible. '
            '(e.g. `biohub.forum` for the default forum module)')
        parser.add_argument(
            '--directory',
            dest='target',
            help='Optional destination directory (without the plugin name).')

    def validate_name(self, name):
        if name is None:
            raise CommandError("you must provide a plugin name.")

        if not name.isidentifier():
            raise CommandError(
                "%r is not a valid plugin name. Makre sure the name is a"
                "valid identifier." % name)

    def validate_template(self, target):
        if not path.exists(target):
            raise CommandError(
                "Plugin template directory missing, reinstall biohub "
                "or just manually create the plugin.")

    def validate_mod_path(self, name, mod_path):
        if not mod_path:
            raise CommandError("you must provide a plugin mod_path.")

        try:
            importlib.import_module(mod_path)

            raise CommandError(
                "The mod_path %r is conflicted with another module, "
                "please specify a new one." % mod_path)
        except ImportError:
            pass

        last_section = mod_path.split('.')[-1]

        if name != last_section:
            raise CommandError(
                "The last section of mod_path should be the same as "
                "your plugin name. Unexpectedly got '%s' instead of "
                "'%s'." % (last_section, name))

    def handle(self, name, mod_path, target=None, **options):
        self.verbosity = options['verbosity']

        self.validate_name(name)
        self.validate_mod_path(name, mod_path)

        if target is None:
            top_dir = path.join(os.getcwd(), name)
        else:
            top_dir = path.join(path.abspath(path.expanduser(target)), name)

        try:
            os.makedirs(top_dir)
        except OSError as e:
            if e.errno == errno.EEXIST:
                if os.listdir(top_dir):
                    message = "'%s' already exists." % top_dir
                    raise CommandError(message)
            else:
                raise CommandError(e)

        camel_case_value = ''.join(x for x in name.title() if x != '_')

        context = Context(dict(options, **{
            'plugin_name': name,
            'plugin_directory': top_dir,
            'camel_case_plugin_name': camel_case_value,
            'plugin_mod_path': mod_path
        }), autoescape=False)

        if not settings.configured:
            settings.configure()
            django.setup()

        template_dir = path.join(
            modpath('biohub.core.plugins'), 'plugin_template')
        self.validate_template(template_dir)

        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):

            relative_dir = root[prefix_length:]
            if relative_dir:
                target_dir = path.join(top_dir, relative_dir)
                if not path.exists(target_dir):
                    os.mkdir(target_dir)

            for dirname in dirs[:]:
                if dirname.startswith('.') or dirname == '__pycache__':
                    dirs.remove(dirname)

            for filename in files:
                if filename.endswith(('.pyo', '.pyc', '.py.class')):
                    continue
                old_path = path.join(root, filename)
                new_path = path.join(top_dir, relative_dir,
                                     filename)

                for old_suffix, new_suffix in self.rewrite_template_suffixes:
                    if new_path.endswith(old_suffix):
                        new_path = new_path[:-len(old_suffix)] + new_suffix
                        break

                if path.exists(new_path):
                    raise CommandError("%s already exists." % new_path)

                with io.open(old_path, 'r', encoding='utf-8') as template_file:
                    content = template_file.read()
                template = Engine().from_string(content)
                content = template.render(context)
                with io.open(new_path, 'w', encoding='utf-8') as new_file:
                    new_file.write(content)

                if self.verbosity >= 2:
                    self.stdout.write("Creating %s\n" % new_path)

                try:
                    shutil.copymode(old_path, new_path)
                except OSError:
                    self.stderr.write(
                        "Notice: Couldn't set permission bits on %s. You're "
                        "probably using an uncommon filesystem setup. No "
                        "problem." % new_path, self.style.NOTICE)
