from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from rest_framework.reverse import reverse

from biohub.forum.models import Experience, Brick
from biohub.notices.tool import Dispatcher


@receiver(pre_delete, sender=Brick)
def delete_article_attached_if_brick_is_deleted(instance, **kwargs):
    instance.document.delete()


@receiver(pre_delete, sender=Experience)
def delete_article_attached_if_experience_is_deleted(instance, **kwargs):
    instance.content.delete()


forum_dispatcher = Dispatcher('Forum')


@receiver(post_save, sender=Experience)
def notice_watching_user_when_new_experience_is_posted(instance, created, **kwargs):
    if created:
        # only send notices when a NEW experience is posted
        for user in instance.brick.watch_users.all():
            # avoid sending notice to the author who published the experience
            if user.id == instance.author.id:
                continue
            experience_url = reverse('api:forum:experience-detail', kwargs={'pk': instance.id})
            brick = instance.brick
            brick_url = reverse('api:forum:brick-detail', kwargs={'pk': brick.id})
            forum_dispatcher.send(
                user,
                'New experience (Title: '
                '{{experience.title|url:experience_url}}) was published '
                'under brick BBA_{{brick.name|url:brick_url}}.',
                experience=instance, experience_url=experience_url,
                brick=brick, brick_url=brick_url
            )
