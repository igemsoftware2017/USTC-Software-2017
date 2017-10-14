import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import biohub.compat  # noqa
from channels.asgi import get_channel_layer  # noqa


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biohub.main.settings.prod")
os.environ.setdefault(
    "BIOHUB_CONFIG_PATH",
    os.path.join(os.path.dirname(__file__), '..', '..', "config.json")
)

channel_layer = get_channel_layer()
