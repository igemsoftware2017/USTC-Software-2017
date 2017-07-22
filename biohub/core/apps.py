from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class CoreConfig(AppConfig):

    name = 'biohub.core'
    label = 'biohub_core'

    def ready(self):
        autodiscover_modules('urls')
