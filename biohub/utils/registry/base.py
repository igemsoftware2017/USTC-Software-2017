from weakref import WeakValueDictionary

from django.dispatch import Signal
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
        self.mapping = WeakValueDictionary()

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


class SignalRegistryBase(RegistryBase):

    providing_args = None

    def __init__(self):
        self.signal_mapping = {}

    @staticmethod
    def is_registered(func):
        return hasattr(func, '_signal_receiver')

    def cache_clear(self, populate=True):
        self.signal_mapping.clear()

        if populate:
            self.populate_submodules()

    def register(self, key, func):

        if key not in self.signal_mapping:
            self.signal_mapping[key] = Signal(providing_args=self.providing_args)  # noqa

        signal = self.signal_mapping[key]

        def _receiver(sender, **kwargs):

            args = (kwargs.get(k, None) for k in self.providing_args)

            func(*args)

        func._signal_receiver = (key, _receiver)

        signal.connect(_receiver)

        self.perform_register(key, func)

    def perform_register(self, key, func):
        pass

    def unregister(self, func):

        if not self.is_registered(func):
            return

        key, receiver = func._signal_receiver

        if key not in self.signal_mapping:
            return

        self.signal_mapping[key].disconnect(receiver)

        self.perform_unregister(func)

    def perform_unregister(self, func):
        pass

    @cached_property
    def register_decorator(self):

        def decorator_factory(key):

            def decorator(func):

                self.register(key, func)

                return func

            return decorator

        return decorator_factory

    def dispatch(self, key, **kwargs):

        if key not in self.signal_mapping:
            return

        self.signal_mapping[key].send(self.__class__, **kwargs)
