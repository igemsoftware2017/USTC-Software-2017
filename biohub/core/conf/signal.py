import signal
import warnings

from biohub.core.conf import load_config
from biohub.core.plugins import plugins


def reload_handler(signum, frame):
    """
    To reload config files and corresponding components when received SIGUSR1
    signal.
    """
    load_config()
    plugins.reload_plugins()


def register():
    if not hasattr(signal, 'SIGUSR1'):
        warnings.warn(
            "Your system doesn't support SIGUSR1, and thus biohub cannot "
            "reload itself at runtime.")
        return

    signal.signal(signal.SIGUSR1, reload_handler)
