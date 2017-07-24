from .config import PluginConfig  # noqa: F401
from .registry import manager as plugins

install = plugins.install
remove = plugins.remove
prepare_database = plugins.prepare_database

default_app_config = 'biohub.core.plugins.apps.PluginsConfig'
