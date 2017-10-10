import json
import os.path as path

from django.utils.functional import SimpleLazyObject, empty
from django.core.validators import ValidationError, URLValidator

from . import consts

dirname = path.dirname(path.abspath(__file__))
config_location = path.join(dirname, 'config.json')


class Settings(SimpleLazyObject):
    """
    A lazy config object providing attribute-like items accessing.
    """

    def _check_local_availability(self, config):
        """
        Check if local ABACUS environment is ready.
        """
        import os
        import subprocess

        # Check if java is ready
        p = subprocess.Popen(['java', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.communicate()

        java_exists = p.returncode == 0

        return java_exists and \
            os.path.isfile(config.get('ABACUS_JAR_PATH', '')) and \
            os.path.isfile(config.get('ABACUS_DATABASE_PATH', ''))

    def _check_remote_availability(self, config):
        """
        Check if remote ABACUS environment is ready.
        """
        try:
            validator = URLValidator()
            for url in config.get('ABACUS_REMOTE_SERVERS', ['']):
                validator(url)

            return True
        except ValidationError:
            return False

    def _load_config(self):
        """
        Startup script.
        """
        with open(config_location, 'r') as fp:
            result = json.load(fp)

        if self._check_local_availability(result):
            result['ident'] = consts.LOCAL
        elif self._check_remote_availability(result):
            result['ident'] = consts.REMOTE
        else:
            raise RuntimeError('Neither local nor remote ABACUS service is available.')

        return result

    def __init__(self):
        super(Settings, self).__init__(self._load_config)  # Set startup script

    def __getattr__(self, name):
        if self._wrapped is empty:
            self._setup()

        result = self._wrapped.get(name, None)
        if result is None:
            result = getattr(self._wrapped, name)

        return result


settings = Settings()
