from biohub.core.routes import register_api, url

from .views import plugins_list, init_plugin, plugin_admin, upgrade_plugin, remove_plugin, plugin_info

register_api(r'^plugins/', [
    url(r'^$', plugins_list, name='list'),
    url(r'^init/$', init_plugin, name='init'),
    url(r'^upgrade/$', upgrade_plugin, name='upgrade'),
    url(r'^remove/$', remove_plugin, name='remove'),
    url(r'^info/$', plugin_info, name='info'),
    url(r'^__admin/$', plugin_admin, name='admin'),
], namespace='plugins')
