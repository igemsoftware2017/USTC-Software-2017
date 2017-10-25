from biohub.core.plugins import PluginConfig


class BiocircuitConfig(PluginConfig):

    name = 'biohub.biocircuit'
    title = 'Biocircuit'
    author = 'zml, wxq'
    description = 'The design of robust and sensitive biological circuit are always bothering. To rationally design synthetic gene circuits with specific functions, we write BioCircuit. The plugin is an adpatation of the project BioBLESS developed by USTC-Software 2015, with the ability to design digital circuit, biological circuit as well as analyze the performance of them.'
    js_url = 'https://ustc-software2017-frontend.github.io/biohub-plugin-bioBLESS/build/plugin.js'
