from django.dispatch import receiver
from django.db.models.signals import pre_delete, m2m_changed, post_save

from biohub.accounts.models import User
from biohub.forum.models.bio_models import Brick

@receiver(pre_delete,sender=Brick)
def move_internal_parts_to_extern(instance, **kwargs):
    """
    called when a part is deleted, the device containing it will move the part to external field
    """
    if(instance.ispart and instance.internal_part_to):
        device = instance.internal_part_to
        device.external_parts += ','+instance.name #add texts to external parts
        device.save()