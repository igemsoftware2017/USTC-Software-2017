from django.dispatch import receiver
from django.db.models.signals import post_save

from biohub.forum.models import Experience
from biohub.notices.tool import Dispatcher


forum_dispatcher = Dispatcher('Forum')


@receiver(post_save, sender=Experience)
def notice_watching_user_when_new_experience_is_posted(instance, created, **kwargs):
    if created:
        # only send notices when a NEW experience is posted
        users_to_send = instance.brick.users_watching.only('id')

        if instance.author is not None:
            users_to_send = users_to_send.exclude(pk=instance.author.id)

        forum_dispatcher.group_send(
            users_to_send,
            '{{experience.author.username|url:experience.author}} '
            'published a new experience {{experience.title|url:experience}} '
            'at brick {{brick.part_name|url:brick}}.',
            experience=instance,
            brick=instance.brick
        )
