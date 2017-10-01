from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.reverse import reverse

from biohub.forum.models import Experience
from biohub.notices.tool import Dispatcher


forum_dispatcher = Dispatcher('Forum')


@receiver(post_save, sender=Experience)
def notice_watching_user_when_new_experience_is_posted(instance, created, **kwargs):
    if created:
        # only send notices when a NEW experience is posted
        for user in instance.brick.users_watching.all():
            # avoid sending notice to the author who published the experience
            if user.id == instance.author.id:
                continue
            experience_url = reverse('api:forum:experience-detail', kwargs={'pk': instance.id})
            brick = instance.brick
            brick_url = reverse('api:forum:biobrick-detail', kwargs={'pk': brick.part_name})
            forum_dispatcher.send(
                user,
                'New experience (Title: '
                '{{experience.title|url:experience_url}}) was published '
                'under brick {{brick.part_name|url:brick_url}}.',
                experience=instance, experience_url=experience_url,
                brick=brick, brick_url=brick_url
            )
