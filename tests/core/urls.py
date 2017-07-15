from biohub.core.routes import url, register_default, register_api

register_default('test/', [
    url('a/$', lambda r: None, name='a'),
], namespace='test')


register_api('test/', [
    url('a/$', lambda r: None, name='a'),
], namespace='test')
