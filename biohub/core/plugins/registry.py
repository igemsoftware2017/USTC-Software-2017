import sys
import subprocess
import threading
import logging
import importlib
from collections import OrderedDict, namedtuple, Counter

from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.conf import settings as django_settings
from django.apps import registry as apps_registry
from django.apps.config import AppConfig

from biohub.utils import module as module_util, path as path_util
from biohub.utils.collections import unique
from biohub.core.conf import settings as biohub_settings, dump_config

from .config import PluginConfig
from . import exceptions

logger = logging.getLogger('biohub.plugins')

REQUIRED_PROPERTIES = ('title', 'author', 'description',)

PluginInfo = namedtuple('PluginInfo', REQUIRED_PROPERTIES)

manage_py_file_path = path_util.join(django_settings.BIOHUB_DIR, 'manage.py')


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

    class _Protect:
        """
        A context manager to protect plugins installation state while
        installing / removing plugins.
        """

        def __init__(self, manager, test=False, config=False):
            self._test = test
            self._manager = manager
            self._config = config
            self._apps = manager._apps

        def __enter__(self):
            self.acquire()

        def acquire(self):
            self._store_app_configs = [
                ac.name for ac in self._apps.app_configs.values()]

            if self._config:
                biohub_settings.store_settings()

        def release(self):
            apps = self._apps
            apps.apps_ready = apps.models_ready = apps.ready = False
            self._manager._populate_apps(self._store_app_configs)
            self._manager.populate_plugins()

            if self._config:
                biohub_settings.restore_settings()

        def __exit__(self, exc_type, exc, traceback):
            if self._test or exc is not None:
                self.release()
            elif self._config:
                biohub_settings.restore_settings(write=False)

    def protect(self, test=False, config=False):

        return self._Protect(self, test, config)

    def __init__(self, apps):
        self.plugin_configs = OrderedDict()
        self.plugin_infos = OrderedDict()
        self._install_lock = threading.Lock()
        self._db_lock = threading.Lock()
        self._apps = apps

    @property
    def installing(self):
        """
        Returns a bool indicating whether plugin list is mutating.
        """
        return self._install_lock.locked()

    @property
    def migrating(self):
        """
        Returns a bool indicating whether there are any plugins migrating their
        models.
        """
        return self._db_lock.locked()

    @property
    def available_plugins(self):
        """
        An alias to biohub_settings.BIOHUB_PLUGINS
        """
        return biohub_settings.BIOHUB_PLUGINS

    @property
    def installed_apps(self):
        return [ac.name for ac in self._apps.app_configs.values()]

    @property
    def apps_to_populate(self):
        """
        Returns the names of apps to be populated.
        """

        return unique(django_settings.INSTALLED_APPS + self.available_plugins)

    def _remove_apps(self, to_remove):
        """
        A shortcut for `_populate_apps`.
        """
        to_remove = set(to_remove)

        return self._populate_apps([
            x for x in self.installed_apps if x not in to_remove])

    def _add_apps(self, to_add):
        """
        A shortcut for `_populate_apps`.
        """
        return self._populate_apps(unique(self.installed_apps + to_add))

    def _populate_apps(self, apps_list):
        """
        A function to more efficiently manipulate django app list.
        """
        apps = self._apps

        missing = set(self.installed_apps) - set(apps_list)
        new = set(apps_list) - set(self.installed_apps)

        apps.apps_ready = apps.models_ready = apps.ready = False

        with apps._lock:

            for entry in apps_list + list(self.installed_apps):

                if isinstance(entry, AppConfig):
                    app_config = entry
                else:
                    app_config = AppConfig.create(entry)

                label = app_config.label

                if entry in missing and label in apps.app_configs:
                    del apps.app_configs[label]
                elif entry in new and label not in apps.app_configs:
                    apps.app_configs[label] = app_config
                    app_config.apps = apps

            counts = Counter(
                app_config.name for app_config in apps.app_configs.values())
            duplicates = [
                name for name, count in counts.most_common() if count > 1]
            if duplicates:
                raise ImproperlyConfigured(
                    "Application names aren't unique, "
                    "duplicates: %s" % ", ".join(duplicates))

            apps.apps_ready = True

            for app_config in apps.app_configs.values():
                app_config.import_models()

            apps.clear_cache()

            apps.models_ready = True

            for app_config in apps.get_app_configs():
                if app_config.name in new:
                    app_config.ready()

            apps.ready = True

    def populate_plugins(self):
        """
        Update plugins storage after new plugins installed.
        """
        self._invalidate_components()

        self.plugin_infos = OrderedDict()
        self.plugin_configs = OrderedDict()
        self.available_plugins.clear()

        for app_config in self._apps.app_configs.values():

            if isinstance(app_config, PluginConfig):
                self._populate_plugin(app_config)
                self.available_plugins.append(app_config.name)

    def _populate_plugin(self, plugin_config):
        """
        Populate a single plugin.
        """

        plugin_name = plugin_config.name
        self.plugin_configs[plugin_name] = plugin_config

        properties = (getattr(plugin_config, pname)
                      for pname in REQUIRED_PROPERTIES)

        self.plugin_infos[plugin_name] = PluginInfo(*properties)

    def _validate_plugins(self, plugin_names):
        """
        Filter and wipe out existing plugins.
        """
        plugin_names = [plugin for plugin in plugin_names
                        if plugin not in self.installed_apps]

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

    def _invalidate_components(self):
        """
        Reloads essential modules or variables in each plugin.
        """
        self._invalidate_urlconf()
        self._invalidate_websocket_handlers()

    def _invalidate_websocket_handlers(self):
        """
        To invalidate websocket handlers registration.
        """
        from biohub.core.websocket.registry import cache_clear
        cache_clear()

    def _invalidate_urlconf(self):
        """
        To invalidate url patterns after plugin list mutated.

        The function will do the following things:

         + invalidate resolver's LRU cache (use `.cache_clear` provided by
            `lru_cache`)
         + reload main urlconf module and clear cache in biohub url patterns
            registration module
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
            biohub.core.routes.cache_clear()
            main_urls = importlib.reload(biohub.main.urls)

            resolver = get_resolver()
            resolver.urlconf_module = main_urls
            resolver.url_patterns = getattr(main_urls, "urlpatterns")

        except Exception as e:
            raise exceptions.URLConfError(e)

    def remove(self, plugin_names,
               update_config=False,
               populate=True,
               invalidate_urlconf=True):
        """
        Remove a list of plugins specified by `plugin_names`.
        """

        with self._install_lock, self.protect(config=update_config):

            removed = list(set(plugin_names) & set(self.installed_apps))

            # halt if no plugins to be REALLY removed
            if not removed:
                return removed

            self._remove_apps(removed)

            if populate:
                self.populate_plugins()

            if update_config:
                dump_config()

        return removed

    def install(self, plugin_names,
                update_config=False,
                populate=True,
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

        if not plugin_names:
            return plugin_names

        with self._install_lock, self.protect(config=update_config):

            # Update django apps list.
            if not self._apps.ready:
                raise exceptions.InstallationError(
                    "Django app registry isn't ready yet.")

            self._add_apps(plugin_names)

            # Migrate database
            if migrate_database:
                self.prepare_database(plugin_names, **(migrate_options or {}))

            if populate:
                self.populate_plugins()

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
                manage_py_file_path,
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


manager = PluginManager(apps_registry.apps)
