import sys
import subprocess
import threading
from collections import OrderedDict, namedtuple

from django.core.management import call_command
from django.conf import settings
from django.apps import apps

from biohub.utils import module as module_util
from biohub.core.conf import settings as biohub_settings, dump_config

from .config import PluginConfig
from . import exceptions


REQUIRED_PROPERTIES = ('title', 'author', 'description',)

PluginInfo = namedtuple('PluginInfo', REQUIRED_PROPERTIES)


def validate_plugin_config(plugin_name, config_class):
    """
    Check if given plugin config class is valid.

    A plugin config class is valid if:

     + it's a subclass of `biohub.core.plugins.PluginConfig`
     + it has all the properties specified in `REQUIRED_PROPERTIES`
    """

    if not issubclass(config_class, PluginConfig):
        raise exceptions.InstallationError(
            "The default config class of plugin '%s' is not a "
            "subclass of `biohub.core.plugins.PluginConfig`."
            % plugin_name)

    missing_fields = set(REQUIRED_PROPERTIES) - set(dir(config_class))

    if missing_fields:
        raise exceptions.InstallationError(
            "Required fields %s missing in config of plugin '%s'"
            % (', '.join(missing_fields), plugin_name))


class PluginManager(object):

    def __init__(self):
        self.plugins = OrderedDict()
        self.plugin_infos = OrderedDict()
        self._install_lock = threading.Lock()
        self._db_lock = threading.Lock()

    @property
    def installing(self):
        return self._install_lock.locked

    @property
    def migrating(self):
        return self._db_lock.locked

    def populate_plugins(self, plugin_names):
        """
        Update plugins storage after new plugins installed.
        """
        for app_config in apps.app_configs.values():

            if app_config.name in plugin_names:
                self._populate_plugin(app_config.name, app_config)

    def _populate_plugin(self, plugin_name, plugin_config):

        self.plugins[plugin_name] = plugin_config

        properties = (getattr(plugin_config, pname)
                      for pname in REQUIRED_PROPERTIES)

        self.plugin_infos[plugin_name] = PluginInfo(*properties)

    def _validate_plugins(self, plugin_names):
        """
        Filter and wipe out existing plugins.
        """
        plugin_names = [plugin for plugin in plugin_names
                        if plugin not in settings.INSTALLED_APPS]

        for name in plugin_names:

            if not module_util.is_valid_module_path(name):
                raise exceptions.InstallationError(
                    "'%s' is not a valid dot-separated python module path."
                    % name)

            # Get the plugin config class
            plugin_config_path = module_util.module_from_path(name)\
                .default_app_config
            plugin_config_class = module_util.object_from_path(
                plugin_config_path)

            validate_plugin_config(name, plugin_config_class)

        return plugin_names

    def _invalidate_urlconf(self, plugin_names):
        """
        Django uses LRU Cache Strategy to cache up resolvers.
        The cache content can be cleared by calling `.cache_clear()`.
        """
        from django.urls.resolvers import get_resolver

        try:
            get_resolver.cache_clear()
        except Exception as e:
            raise exceptions.URLConfError(e)

    def install(self, plugin_names,
                update_config=False,
                invalidate_urlconf=True,
                migrate_database=False, migrate_options=None):
        """
        Install a list of plugins specified by `plugin_names`.

        `plugin_names` should be a list of dot-separated python module path,
        existing plugins will be ignored.

        By setting `invalidate_urlconf` to True (default), biohub will
        automatically update the URLConf after the plugins populated.

        By setting `migrate_database` to True (default to False), biohub will
        automatically migrate models of the plugins. Extra migration options
        can be specified using `migrate_options` (should be a dict).
        """

        plugin_names = self._validate_plugins(plugin_names)

        with self._install_lock:

            if not plugin_names:
                return plugin_names

            # Update django apps list.
            if not apps.ready:
                raise exceptions.InstallationError(
                    "Django app registry isn't ready yet.")

            apps.app_configs = OrderedDict()
            apps.apps_ready = apps.models_ready = apps.ready = False

            try:
                apps.clear_cache()
                apps.populate(list(settings.INSTALLED_APPS) + plugin_names)
            except Exception as e:
                raise exceptions.InstallationError(e)

            # Invalidate URLConf
            if invalidate_urlconf:
                self._invalidate_urlconf(plugin_names)

            # Migrate database
            if migrate_database:
                self.prepare_database(plugin_names, **(migrate_options or {}))

            self.populate_plugins(plugin_names)

            biohub_settings.BIOHUB_PLUGINS.extend(plugin_names)
            if update_config:
                dump_config()

        return plugin_names

    def prepare_database(self, plugin_names, new_process=False,
                         no_input=False, no_output=False,
                         verbosity=0, test=False):
        """
        The function is to migrate models of plugins specified by
        `plugin_names`.
        Note that it will not check whether the plugins are installed or not.

        The function is actually a wrapper of biohub command `migrateplugin`.

        By setting `new_process` to True (default to False), the function will
        start up the migration in a subprocess instead of directly calling
        `call_command`. This may be useful while testing, especially if your
        test runner bans migration.

        The rest arguments has the same meaning as those in command
        `migrateplugin`.
        """

        with self._db_lock:
            try:
                for plugin in plugin_names:

                    self._migrate_plugin(
                        plugin, new_process,
                        no_input, no_output,
                        verbosity, test)

            except Exception as e:
                raise exceptions.DatabaseError(e)

    def _migrate_plugin(self, plugin_name, new_process=False,
                        no_input=False, no_output=False,
                        verbosity=0, test=False):
        if new_process:
            args = filter(bool, [
                'manage.py',
                'migrateplugin',
                plugin_name,
                '--verbosity=%s' % verbosity,
                '--no-input' if no_input else '',
                '--no-output' if no_output else '',
                '--test' if test else ''
            ])

            p = subprocess.Popen(
                list(args),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            sys.stdout.write(stdout.decode('utf-8'))
            sys.stderr.write(stderr.decode('utf-8'))
        else:
            call_command(
                'migrateplugin', plugin_name,
                interactive=no_input,
                no_output=no_output,
                verbosity=verbosity,
                test=test)


manager = PluginManager()
