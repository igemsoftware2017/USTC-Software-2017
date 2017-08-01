from django.dispatch import receiver
from django.db.models.signals import pre_delete
from biohub.forum.models import Experience, Brick


@receiver(pre_delete, sender=Brick)
def delete_article_attached_if_brick_is_deleted(instance, **kwargs):
    instance.document.delete()


@receiver(pre_delete, sender=Experience)
def delete_article_attached_if_experience_is_deleted(instance, **kwargs):
    instance.content.delete()
