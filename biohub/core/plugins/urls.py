from biohub.core.routes import register_api, url

from .views import plugins_list

register_api(r'^plugins/', [
    url(r'^$', plugins_list, name='list')
], namespace='plugins')
