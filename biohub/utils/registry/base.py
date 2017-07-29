from collections import OrderedDict

from django.utils.functional import cached_property

from biohub.utils.module import autodiscover_modules


class RegistryBase(object):

    submodules_to_populate = ()

    @classmethod
    def populate_submodules(cls):

        autodiscover_modules(*cls.submodules_to_populate)


class ListRegistryBase(RegistryBase):

    def __init__(self):
        self.storage_list = []

    def cache_clear(self, populate=True):
        self.storage_list.clear()
        if populate:
            self.populate_submodules()

    def register(self, lst):
        self.storage_list.extend(lst)

        for item in lst:
            self.perform_register(item)

    def perform_register(self, item):
        pass


class DictRegistryBase(RegistryBase):

    def __init__(self):
        self.mapping = OrderedDict()

    def cache_clear(self, populate=True):
        self.mapping.clear()
        if populate:
            self.populate_submodules()

    def register(self, key, value):

        if key in self.mapping:
            raise KeyError("Key '%s' conflicted." % key)

        self.mapping[key] = value

        self.perform_register(key, value)

    def perform_register(self, key, value):
        pass

    def unregister(self, key):
        self.mapping.pop(key, None)

        self.perform_unregister(key)

    def perform_unregister(self, key):
        pass

    @cached_property
    def register_decorator(self):

        def decorator_factory(key):

            def decorator(value):

                self.register(key, value)

                return value

            return decorator

        return decorator_factory

    def __getitem__(self, key):
        return self.mapping[key]
