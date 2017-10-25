from biohub.core.plugins import PluginConfig


class AbacusConfig(PluginConfig):

    name = 'biohub.abacus'
    title = 'ABACUS'
    author = 'Jay Lan, Jiansi Li, hsfzxjy'
    description = 'ABACUS is a tool to design amino acid sequence from a given protein. Proteins are specified in Protein Data Bank format. The uploaded .pdb will be evaludated by simulated annealing algorithm, and another .pdb file representing the result will be returned.'
    js_url = 'https://ustc-software2017-frontend.github.io/biohub-plugin-ABACUS/build/plugin.js'
