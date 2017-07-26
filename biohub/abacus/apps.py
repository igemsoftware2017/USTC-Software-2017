import os
from biohub.core.plugins import PluginConfig


class AbacusConfig(PluginConfig):
    name = 'biohub.abacus'
    title = 'ABACUS'
    author = 'Jay Lan, Jiansi Li'
    description = 'abacus'

    app_path = os.getcwd()
