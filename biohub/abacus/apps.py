import os
from biohub.core.plugins import PluginConfig


class AbacusConfig(PluginConfig):
    name = 'abacus'
    title = 'ABACUS'
    author = 'Jay Lan, Jisi Li'
    description = 'abacus'

    app_path = os.getcwd()
