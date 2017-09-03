from django.apps import AppConfig


class ForumConfig(AppConfig):
    name = 'biohub.forum'
    times_calling_ready_method = 0

    def ready(self):
        # avoid executing for more than once
        ForumConfig.times_calling_ready_method += 1
        if ForumConfig.times_calling_ready_method <= 1:
            from biohub.forum import signals  # noqa
