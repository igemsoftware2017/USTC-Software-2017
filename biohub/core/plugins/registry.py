import sys
import subprocess
import threading
import logging
import importlib
from collections import OrderedDict, namedtuple

from django.core.management import call_command
from django.conf import settings
from django.apps import apps

from biohub.utils import module as module_util
from biohub.utils.collections import unique
from biohub.core.conf import settings as biohub_settings, dump_config

from .config import PluginConfig
from . import exceptions

logger = logging.getLogger('biohub.plugins')

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
        """
        Returns a bool indicating whether plugin list is mutating.
        """
        return self._install_lock.locked

    @property
    def migrating(self):
        """
        Returns a bool indicating whether there are any plugins migrating their
        models.
        """
        return self._db_lock.locked

    @property
    def available_plugins(self):
        """
        An alias to biohub_settings.BIOHUB_PLUGINS
        """

        if not hasattr(self, '_available_plugins'):
            self._available_plugins = biohub_settings.BIOHUB_PLUGINS

        return self._available_plugins

    @property
    def apps_to_populate(self):
        """
        Returns the names of apps to be populated.
        """

        return unique(settings.INSTALLED_APPS + self.available_plugins)

    def populate_plugins(self, plugin_names):
        """
        Update plugins storage after new plugins installed.
        """
        for app_config in apps.app_configs.values():

            if app_config.name in plugin_names:
                self._populate_plugin(app_config.name, app_config)

    def _populate_plugin(self, plugin_name, plugin_config):
        """
        Populate a single plugin.
        """

        self.plugins[plugin_name] = plugin_config

        properties = (getattr(plugin_config, pname)
                      for pname in REQUIRED_PROPERTIES)

        self.plugin_infos[plugin_name] = PluginInfo(*properties)

    def _validate_plugins(self, plugin_names):
        """
        Filter and wipe out existing plugins.
        """
        plugin_names = [plugin for plugin in plugin_names
                        if plugin not in self.available_plugins]

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

    def _invalidate_urlconf(self):
        """
        To invalidate url patterns after plugin list mutated.

        The function will do the following things:

         + invalidate resolver's LRU cache (use `.cache_clear` provided by
            `lru_cache`)
         + reload main urlconf module and biohub url patterns registration
            module
         + reload `urls.py` in each app, using a force-reload version of
            `autodiscover_module`
         + override default resolver's `urlconf_module` and `url_patterns`
            attributes, which are cached property and must be explicitly
            assigned
        """
        from django.urls.resolvers import get_resolver
        import biohub.core.routes
        import biohub.main.urls

        try:
            get_resolver.cache_clear()

            importlib.reload(biohub.core.routes)
            main_urls = importlib.reload(biohub.main.urls)
            module_util.autodiscover_modules('urls')

            resolver = get_resolver()
            resolver.urlconf_module = main_urls
            resolver.url_patterns = getattr(
                main_urls, "urlpatterns", main_urls)

        except Exception as e:
            raise exceptions.URLConfError(e)

    def remove(self, plugin_names,
               update_config=False,
               invalidate_urlconf=True):
        """
        Remove a list of plugins specified by `plugin_names`.
        """

        with self._install_lock:

            removed = []

            for plugin_name in plugin_names:
                try:
                    self.available_plugins.remove(plugin_name)
                    removed.append(plugin_name)
                except ValueError:
                    pass

            # halt if no plugins to be REALLY removed
            if not removed:
                return removed

            if apps.ready:
                apps.app_configs = OrderedDict()
                apps.apps_ready = apps.models_ready = apps.ready = False

                try:
                    apps.clear_cache()
                    apps.populate(self.apps_to_populate)
                except Exception as e:
                    raise exceptions.RemovalError(e)

            if invalidate_urlconf:
                self._invalidate_urlconf()

            # update plugin infos
            for plugin_name in removed:
                self.plugin_infos.pop(plugin_name, 0)

            if update_config:
                dump_config()

        return removed

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
                apps.populate(self.apps_to_populate + plugin_names)
            except Exception as e:
                raise exceptions.InstallationError(e)

            # Invalidate URLConf
            if invalidate_urlconf:
                self._invalidate_urlconf()

            # Migrate database
            if migrate_database:
                self.prepare_database(plugin_names, **(migrate_options or {}))

            self.populate_plugins(plugin_names)

            self.available_plugins.extend(plugin_names)

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
            except exceptions.DatabaseError as e:
                raise e
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

            if p.returncode != 0:
                raise exceptions.DatabaseError(
                    'Migration processreturns non-zero exit code.')
        else:
            call_command(
                'migrateplugin', plugin_name,
                interactive=no_input,
                no_output=no_output,
                verbosity=verbosity,
                test=test)


manager = PluginManager()