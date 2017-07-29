from biohub.core.plugins import PluginConfig


class cleanunusedTestsConfig(PluginConfig):

    name = 'tests.core.files.cleanunused_tests'
    label = 'cleanunused_tests'
    title = ''
    author = ''
    description = ''

    clean_unused = [
        ('TestModel', {'text': r'\[(.*?)\]\(.*?\)'})
    ]
