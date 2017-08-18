"""
This module provides base classes with various implementation for objects
registration.
"""

from weakref import WeakValueDictionary

from django.dispatch import Signal
from django.utils.functional import cached_property

from biohub.utils.module import autodiscover_modules


class RegistryBase(object):
    """
    The base class of all registries.

    A registry class should define a `register` function, while unregistration
    functionality is unnecessary.

    Considered that users may place registration operations in some custom
    submodules where django will not automatically discover, the class provides
    a `populate_submodules` class method for convenience. Subclasses may define
    the class property `submodules_to_populate` to specify names of submodules
    to be populated.
    """

    submodules_to_populate = ()

    @classmethod
    def populate_submodules(cls):

        autodiscover_modules(*cls.submodules_to_populate)

    def cache_clear(self, populate=True):
        """
        Clears inner storage.

        By setting argument `populate` to True (default), the function will
        automatically populate submodules right after cache cleared.
        """
        self.perform_cache_clear()

        if populate:
            self.populate_submodules()

    def perform_cache_clear(self):
        pass


class ListRegistryBase(RegistryBase):
    """
    A registry class with list-based item storage.

    Note that it DOES NOT do any duplication check, nor does it have the
    ability to unregister an item.
    """

    def __init__(self):
        self.storage_list = []

    def perform_cache_clear(self):
        self.storage_list.clear()

    def register(self, seq):
        """
        Given a sequence, simply appends its items to the registry storage.
        """
        self.storage_list.extend(seq)

        for item in seq:
            self.perform_register(item)

    def perform_register(self, item):
        pass


class MappingRegistryMixin(object):
    """
    A mixin class for mapping-like registry to provide decorator for
    registration.
    """

    @cached_property
    def register_decorator(self):

        def decorator_factory(key):

            def decorator(value):
                self.register(key, value)
                return value

            return decorator

        return decorator_factory


class DictRegistryBase(RegistryBase, MappingRegistryMixin):
    """
    A registry class with dict-based item storage.

    Note that the registry just owns a weak reference to the items.
    """

    key_error_class = KeyError

    def __init__(self):
        self.mapping = WeakValueDictionary()

    def perform_cache_clear(self):
        self.mapping.clear()

    def register(self, key, value):
        """
        Registration.

        If the given key has already existed, the function will raise a
        KeyError.
        """

        if key in self.mapping:
            raise self.key_error_class(key)

        self.mapping[key] = value
        self.perform_register(key, value)

    def perform_register(self, key, value):
        pass

    def unregister(self, key):
        """
        Unregistration.

        If the given key does not exist, the function will fail silently.
        """
        self.mapping.pop(key, None)

        self.perform_unregister(key)

    def perform_unregister(self, key):
        pass

    def __getitem__(self, key):
        """
        Shortcuts to access registered items.
        """
        return self.mapping[key]


class SignalRegistryBase(RegistryBase, MappingRegistryMixin):
    """
    A registry class based on django signal system, having the ability to
    create many-to-many connections between keys and callables.

    Note that the items MUST be callables.
    """

    # Subclasses may override this property to specify names of arguments
    # passed to handlers.
    providing_args = None

    def __init__(self):
        self.signal_mapping = {}

    def perform_cache_clear(self):
        self.signal_mapping.clear()

    def perform_register(self, key, func):
        pass

    def perform_unregister(self, func):
        pass

    @cached_property
    def func_property_name(self):
        """
        The name of the hidden property to be attached to registered function.
        """
        return '_signal_receiver_%s' % id(self)

    def is_registered(self, func):
        """
        Checks if the function has been register.
        """
        return hasattr(func, self.func_property_name)

    def register(self, key, func):
        """
        Registration.

        For a specific registry instance, a function can only be registered
        ONCE, otherwise a KeyError will be raised.
        """

        if hasattr(func, self.func_property_name):
            raise KeyError('Function %r has been registered.' % func)

        if key not in self.signal_mapping:
            self.signal_mapping[key] = Signal(providing_args=self.providing_args)  # noqa

        # The receiver function to be connected to a signal
        def _receiver(sender, **kwargs):
            args = (kwargs.get(k, None) for k in self.providing_args)
            func(*args)

        # Attach the receiver onto the function to avoid garbage collection.
        setattr(func, self.func_property_name, (key, _receiver))
        self.signal_mapping[key].connect(_receiver)

        self.perform_register(key, func)

    def unregister(self, func):
        """
        Unregistration.
        """

        if not self.is_registered(func):
            return

        key, receiver = getattr(func, self.func_property_name)

        if key not in self.signal_mapping:
            return

        # Drop the attached reference on the function.
        delattr(func, self.func_property_name)
        self.signal_mapping[key].disconnect(receiver)

        self.perform_unregister(func)

    def dispatch(self, key, **kwargs):
        """
        Dispatches arguments to all handlers related with the given key.
        """

        if key not in self.signal_mapping:
            return

        self.signal_mapping[key].send(self.__class__, **kwargs)
