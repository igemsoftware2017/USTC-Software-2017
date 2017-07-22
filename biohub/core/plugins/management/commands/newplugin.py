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

    help = "Create a new plugin."

    rewrite_template_suffixes = (
        # Allow shipping invalid .py files without byte-compilation.
        ('.py-tpl', '.py'),
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'plugin_name',
            help='Dot-separated python module path referring to the '
            'plugin. NOTE THAT the path should be globally visible and unique.'
            ' (e.g. `biohub.forum` for the default forum module)')
        parser.add_argument(
            '--directory',
            dest='target',
            help='Optional destination directory (without the plugin name).')

    def _validate_template(self, target):
        """
        To ensure that the plugin template directory does exist.
        """

        if not path.exists(target):
            raise CommandError(
                "Plugin template directory missing, reinstall biohub "
                "or just manually create the plugin.")

    def _validate_plugin_name(self, plugin_name):
        """
        To validate the given `plugin_name`.

        A `plugin_name` is considered valid if:

         + it's not empty.
         + it does not exist currently.

        Afterwards the attributes `self.plugin_name` and `self.label` will be
        set.
        """

        if not plugin_name:
            raise CommandError("You must provide a plugin_name.")

        try:
            importlib.import_module(plugin_name)

            raise CommandError(
                "The plugin_name %r is conflicted with another module, "
                "please specify a new one." % plugin_name)
        except ImportError:
            pass

        self.label = plugin_name.rsplit('.', 1)[-1]
        self.plugin_name = plugin_name

    def _prepare_dest_dir(self, target):
        """
        To ensure that the destination directory exists and is prepared.
        """

        if target is None:
            top_dir = path.join(os.getcwd(), self.label)
        else:
            top_dir = path.join(
                path.abspath(path.expanduser(target)),
                self.label)

        try:
            os.makedirs(top_dir)
        except OSError as e:
            if e.errno == errno.EEXIST:
                if os.listdir(top_dir):
                    raise CommandError("'%s' already exists." % top_dir)
            else:
                raise CommandError(e)

        return top_dir

    def _render_plugin_dir(self, top_dir, **options):
        """
        Reference: django.core.management.templates:110

        To copy and render the plugin templates to the destination directory
        specified by `top_dir`.
        """

        camel_case_value = ''.join(x for x in self.label.title() if x != '_')

        context = Context(dict(options, **{
            'plugin_label': self.label,
            'plugin_directory': top_dir,
            'camel_case_plugin_label': camel_case_value,
            'plugin_name': self.plugin_name
        }), autoescape=False)

        if not settings.configured:
            settings.configure()
            django.setup()

        template_dir = path.join(
            modpath('biohub.core.plugins'),
            'plugin_template')
        self._validate_template(template_dir)

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

        if self.verbosity >= 1:
            self.stdout.write(
                "Successfully created a plugin '%s'." % self.plugin_name,
                self.style.SUCCESS)
            self.stdout.write(
                "Notice: Label of the plugin is automatically set to '%s' "
                "(the last section of '%s'). \nIf you are told that the label "
                "conflicts with another app during developing, please specify "
                "a new label by manually add an attribute "
                "`label = '<your new label>'` to `%sConfig` in file '%s'."
                % (
                    self.label,
                    self.plugin_name,
                    camel_case_value,
                    path.join(top_dir, 'apps.py')), self.style.WARNING)

    def handle(self, plugin_name, target=None, **options):

        self.verbosity = options['verbosity']

        self._validate_plugin_name(plugin_name)

        top_dir = self._prepare_dest_dir(target)
        self._render_plugin_dir(top_dir, **options)
