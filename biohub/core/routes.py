"""
By default, Biohub will expose two URL prefixes `^` and `^/api`, where developer
s can register their own urlpatterns by using `register_api` and
`register_default`. This design can prevent plugin authors from directly
modifying the main urlconf.
"""

from django.conf.urls import include, url


class UrlProxy(object):

    def __init__(self, prefix, name=None):
        self.__prefix = prefix
        self.__urls = []
        self.__name = name

    def register(self, prefix, urls, namespace=None):
        """
        Register a list of urlpatterns with given prefix and namespace.
        """
        self.__urls.append(
            url(prefix, include((urls, namespace))))

    @property
    def name(self):
        return self.__name

    @property
    def urls(self):
        return self.__urls

    @property
    def prefix(self):
        return self.__prefix


APIUrlProxy = UrlProxy(r'^api/', 'api')
DefaultUrlProxy = UrlProxy(r'^', 'default')

register_api = APIUrlProxy.register
register_default = DefaultUrlProxy.register

urlpatterns = []

for proxy in (APIUrlProxy, DefaultUrlProxy):
    urlpatterns.append(
        url(proxy.prefix, include(proxy.urls, namespace=proxy.name)))
