import os
import os.path
import json
import filelock
import tempfile

from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import LazyObject, empty

CONFIG_ENVIRON = 'BIOHUB_CONFIG_PATH'
LOCK_FILE_PATH = os.path.join(tempfile.gettempdir(), 'biohub.config.lock')

mapping = {
    'DEFAULT_DATABASE': 'DATABASE',
    'BIOHUB_PLUGINS': 'PLUGINS',
    'TIMEZONE': 'TIMEZONE'
}


class LazySettings(LazyObject):
    """
    A proxy to settings object. Settings will not be loaded until it is
    accessed.
    """

    @property
    def configured(self):
        """
        Returns a boolean indicating whether the settings is loaded.
        """
        return self._wrapped is not empty

    def _setup(self):

        self._wrapped = manager._settings_object
        manager.load()

    def __getattr__(self, name):

        if self._wrapped is empty:
            self._setup()

        val = getattr(self._wrapped, name)
        self.__dict__[name] = val

        return val

    def __setattr__(self, name, value):

        if name == '_wrapped':
            self.__dict__.clear()
        else:
            self.__dict__.pop(name, None)

        super(LazySettings, self).__setattr__(name, value)

    def __delattr__(self, name):

        super(LazySettings, self).__delattr__(name)
        self.__dict__.pop(name, None)


class SettingsManager(object):

    def __init__(self, settings_object):

        self._settings_object = settings_object

        # resolve config_file_path
        if CONFIG_ENVIRON in os.environ:
            config_file_path = os.environ[CONFIG_ENVIRON]

            if not os.path.isfile(config_file_path):
                raise ImproperlyConfigured(
                    "Config file '%s' does not exist or is not a file."
                    % config_file_path)

            self._file_lock = filelock.FileLock(LOCK_FILE_PATH)
        else:
            config_file_path = None

        self.config_file_path = config_file_path
        self._store_settings = []

    def store_settings(self):
        """
        A function for testing, which saves current state of config file.
        """

        if self.config_file_path is None:
            return

        with self._file_lock:
            with open(self.config_file_path, 'r') as fp:
                self._store_settings.append(fp.read())

    def restore_settings(self):
        """
        A function for testing, which restores the state in the last call of
        `store_settings`.
        """

        if self.config_file_path is None:
            return

        with self._file_lock:
            with open(self.config_file_path, 'w') as fp:
                fp.write(self._store_settings.pop())

    def load(self, path=None):
        """
        Load configuration from file specified by `self.config_file_path`.

        The function is thread-safe.
        """

        path = path or self.config_file_path

        if path is None:
            return

        locking = self._file_lock.is_locked

        with self._file_lock:

            if locking:
                return

            with open(path, 'r') as fp:
                fp.seek(0)
                source = json.load(fp)

            self._load_config_from_dict(source)

    def _load_config_from_dict(self, source):

        for name, conf_name in mapping.items():
            setattr(self._settings_object, name,
                    source.get(conf_name,
                               getattr(self._settings_object, name)))

    def dump(self, path=None):
        """
        Write configuration back to file.

        The function is thread-safe.
        """

        path = path or self.config_file_path

        if path is None:
            return

        with self._file_lock:
            with open(path, 'w') as fp:
                json.dump(self._dump_config(), fp, indent=4)

    def _dump_config(self):
        return dict(
            (value, getattr(self._settings_object, key))
            for key, value in mapping.items())


settings = LazySettings()
manager = SettingsManager(Settings())

load_config = manager.load
dump_config = manager.dump
