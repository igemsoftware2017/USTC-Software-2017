from biohub.core.plugins import PluginConfig


class BiomapConfig(PluginConfig):

    name = 'biohub.biomap'
    title = 'BioMap'
    author = 'hsfzxjy'
    description = 'A tool to analyze relationships between bricks. Just input the full name of a specific part (e.g. BBa_B0015) and click the corresponding button, the plugin will show you the relationship between it and other parts.'
    js_url = 'https://ustc-software2017-frontend.github.io/biohub-plugin-BioMap/build/plugin.js'
