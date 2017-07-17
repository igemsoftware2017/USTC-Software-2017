import os


class settings:

    DEFAULT_DATABASE = {}
    BIOHUB_PLUGINS = []
    TIMEZONE = 'UTC'


mapping = {
    'DEFAULT_DATABASE': 'DATABASE',
    'BIOHUB_PLUGINS': 'PLUGINS',
    'TIMEZONE': 'TIMEZONE'
}


def read_config(source):

    global settings

    for name, conf_name in mapping.items():
        setattr(settings, name,
                source.get(conf_name,
                           getattr(settings, name)))


def load_extra_config():
    """
    Loads customized configuration specified via environment
    `BIOHUB_CONFIG_PATH`.
    """

    CONFIG_ENVIRON = 'BIOHUB_CONFIG_PATH'

    if CONFIG_ENVIRON in os.environ:

        import json

        config_path = os.environ[CONFIG_ENVIRON]

        try:
            with open(config_path, 'r') as fp:
                read_config(json.load(fp))

        except OSError as e:

            import errno
            from django.core.exceptions import ImproperlyConfigured

            # Config file not exists
            if e.errno == errno.ENOENT:
                raise ImproperlyConfigured(
                    "Config file %r doesn't exist." % config_path
                )


load_extra_config()
