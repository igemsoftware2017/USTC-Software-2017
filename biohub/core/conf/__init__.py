import os
import os.path
import json
import filelock
import tempfile
import logging
import warnings

from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import LazyObject, empty

from biohub.utils.collections import unique

logger = logging.getLogger('biohub.conf')

CONFIG_ENVIRON = 'BIOHUB_CONFIG_PATH'
LOCK_FILE_PATH = os.path.join(tempfile.gettempdir(), 'biohub.config.lock')

# Field mapping for biohub settings
# Format: dest_name -> (org_name, default)
mapping = {
    'DEFAULT_DATABASE': ('DATABASE', dict),
    'BIOHUB_PLUGINS': ('PLUGINS', list),
    'TIMEZONE': ('TIMEZONE', 'UTC'),
    'UPLOAD_DIR': ('UPLOAD_DIR',
                   lambda: os.path.join(tempfile.gettempdir, 'biohub')),
    'REDIS_URI': ('REDIS_URI', '')
}

valid_settings_keys = tuple(mapping.values())


class BiohubSettingsWarning(RuntimeWarning):

    pass


class Settings(object):
    """
    The core settings class, which can validate, store, serialize/deserialze
    biohub relevant configuration items.
    """

    def _validate(self, key, value):
        """
        A proxy function for validation, which will find `validate_<key>`
        method in self and feed `value` to it if the method exists. The
        validation methods should return the validated value.
        """

        validate_func = getattr(
            self, 'validate_%s' % key.lower(), None)
        if validate_func is not None:
            value = validate_func(value)

        return value

    def _set_settings_values(self, source=None):
        """
        Validate and store configuration items specified by `source` (a dict).

        If source is `None`, the function will use default values to fill up
        unset configuration items.
        """

        if source is None:

            for dest_name, (org_name, default_value) in mapping.items():

                if not hasattr(self, dest_name):
                    value = default_value() if callable(default_value) \
                        else default_value

                    setattr(self, dest_name, value)

            return

        for dest_name, (org_name, default_value) in mapping.items():

            value = source.get(org_name, None)

            if value is None:
                value = default_value() if callable(default_value) \
                    else default_value

            value = self._validate(dest_name, value)

            setattr(self, dest_name, value)

    def dump_settings_value(self):
        """
        Return a dict containing gathered configuration items.
        """

        result = {}

        for dest_name, (org_name, _) in mapping.items():

            value = getattr(self, dest_name)

            value = self._validate(dest_name, value)

            result[org_name] = value

        return result

    def validate_biohub_plugins(self, value):
        """
        BIOHUB_PLUGINS should not contains duplicated items.
        """
        return unique(value)

    def validate_redis_uri(self, value):

        if not value:
            warnings.warn(
                'No redis configuration provided, redis-based services '
                'will be disabled.', BiohubSettingsWarning)

        return value

    def validate_upload_dir(self, value):
        if value.startswith(tempfile.gettempdir()):
            warnings.warn(
                'Your UPLOAD_DIR is within the temporary directory. All '
                'files will be erased once system reboots.',
                BiohubSettingsWarning)

        return os.path.abspath(value)

    def __delattr__(self, name):
        """
        Configuration items should be protected.
        """
        if name in valid_settings_keys:
            raise KeyError(
                "Can't delete a configuration item.")

        super(Settings, self).__delattr__(name)


class LazySettings(LazyObject):
    """
    A proxy to settings object. Settings will not be loaded until it is
    accessed.
    """

    def __init__(self):

        self._manager = SettingsManager(Settings())

        super(LazySettings, self).__init__()

    @property
    def configured(self):
        """
        Returns a boolean indicating whether the settings is loaded.
        """
        return self._wrapped is not empty

    def _setup(self):

        self._wrapped = self._manager._settings_object
        self._manager.load()

    def __getattr__(self, name):

        if self._wrapped is empty:
            self._setup()

        val = getattr(self._manager, name, None)

        if val is None:
            val = getattr(self._wrapped, name)

        return val

    def __setattr__(self, name, value):

        if name == '_manager':
            self.__dict__['_manager'] = value
            return

        self.__dict__.pop(name, None)

        super(LazySettings, self).__setattr__(name, value)

    def __delattr__(self, name):
        raise AttributeError('Not allowed to remove a settings attribute.')


class SettingsManager(object):

    def __init__(self, settings_object):

        self._settings_object = settings_object
        self._file_lock = filelock.FileLock(LOCK_FILE_PATH)
        self._store_settings = []

    @property
    def locking(self):
        return self._file_lock.is_locked

    def _resolve_config_path(self, config_path=None):
        """
        Resolves the path of config file.

        If `config_path` is not None, it will be used. Otherwise
        `os.environ['CONFIG_ENVIRON']` will be used. If both of them are None,
        no config file is specified.

        The path to be used will have existence test before returned.
        """

        if config_path is None:
            config_path = os.environ.get(CONFIG_ENVIRON, None)

        if config_path is not None and not os.path.isfile(config_path):
            raise ImproperlyConfigured(
                "Config file '%s' does not exist or is not a file."
                % config_path)

        self.config_file_path = config_path

        return config_path

    def store_settings(self):
        """
        A function for testing, which saves current state of config file.

        Note that the function MUST be balanced by using `restore_settings`.
        """

        if self.config_file_path is None:
            return

        with self._file_lock:
            with open(self.config_file_path, 'r') as fp:
                self._store_settings.append(fp.read())

    def restore_settings(self, write=True):
        """
        A function for testing, which restores the state in the last call of
        `store_settings`.
        """

        poped = self._store_settings.pop()

        if not write:
            return

        if self.config_file_path is None:
            return

        with self._file_lock:
            with open(self.config_file_path, 'w') as fp:
                fp.write(poped)

    def load(self, path=None):
        """
        Load configuration from file specified by `self.config_file_path`.

        The function is thread-safe.
        """

        path = self._resolve_config_path(path)

        locking = self.locking

        with self._file_lock:

            if locking:
                return

            if path is None:
                source = None
            else:
                with open(path, 'r') as fp:
                    source = json.load(fp)

            self._settings_object._set_settings_values(source)

    def dump(self, path=None):
        """
        Write configuration back to file.

        The function is thread-safe.
        """

        path = self._resolve_config_path(path)

        if path is None:
            return

        with self._file_lock:
            with open(path, 'w') as fp:
                json.dump(
                    self._settings_object.dump_settings_value(),
                    fp, indent=4)


settings = LazySettings()

load_config = settings.load
dump_config = settings.dump
