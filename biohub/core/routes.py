"""
By default, Biohub will expose two URL prefixes `^` and `^/api`, where
developers can register their own urlpatterns by using `register_api` and
`register_default`. This design can prevent plugin authors from directly
modifying the main urlconf.
"""

from django.conf.urls import include, url

from biohub.utils.registry.base import ListRegistryBase


class UrlPatternsRegistry(ListRegistryBase):

    submodules_to_populate = ('urls',)

    def __init__(self, prefix, name=None):
        self.__prefix = prefix
        self.__name = name

        super(UrlPatternsRegistry, self).__init__()

    def register(self, prefix, urls, namespace=None):
        """
        Register a list of urlpatterns with given prefix and namespace.
        """
        super(UrlPatternsRegistry, self).register([
            url(
                prefix,
                include((urls, namespace))
            )
        ])

    @property
    def name(self):
        return self.__name

    @property
    def urls(self):
        return self.storage_list

    @property
    def prefix(self):
        return self.__prefix


api_url_patterns = UrlPatternsRegistry(r'^api/', 'api')
default_url_patterns = UrlPatternsRegistry(r'^', 'default')

register_api = api_url_patterns.register
register_default = default_url_patterns.register

urlpatterns = []

for proxy in (api_url_patterns, default_url_patterns):
    urlpatterns.append(
        url(proxy.prefix, include(proxy.urls, namespace=proxy.name)))


def cache_clear():
    """
    To clear the stored url patterns, used for invalidating.
    """
    for proxy in (api_url_patterns, default_url_patterns):
        proxy.cache_clear(populate=False)

    UrlPatternsRegistry.populate_submodules()
