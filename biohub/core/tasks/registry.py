from biohub.utils.registry.base import DictRegistryBase
from biohub.core.tasks.exceptions import TaskRegistered


class TaskRegistry(DictRegistryBase):

    submodules_to_populate = ('tasks',)
    key_error_class = TaskRegistered


tasks = TaskRegistry()
cache_clear = tasks.cache_clear
