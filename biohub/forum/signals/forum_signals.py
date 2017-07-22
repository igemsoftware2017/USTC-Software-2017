from django.dispatch import receiver
from django.db.models.signals import pre_delete, m2m_changed

from biohub.accounts.models import User
from biohub.forum.models import Thread, Post, Studio, Part


@receiver(pre_delete, sender=Thread)
def hide_attached_posts(instance, **kwargs):
    for post in instance.post_set.all():
        post.hide()


@receiver(pre_delete, sender=Post)
def hide_attached_comments(instance, **kwargs):
    for comment in instance.comments.all():
        comment.hide()


@receiver(pre_delete, sender=Studio)
@receiver(pre_delete, sender=Part)
def hide_attached_threads(instance, **kwargs):
    for thread in instance.thread_set.all():
        thread.hide()


@receiver(m2m_changed, sender=Studio.users.through)
def delete_studio_with_no_user__m2m(instance, pk_set, action, **kwargs):
    # Warning: Because using post_clear signal we can't get pk_set,
    # which means we don't know what relations have been cleared.
    # So please don't use something like user.studio_set.clear()
    # That will leave some empty studio.
    if action != 'post_remove':
        return
    studios = []
    # consider two situations: user.studio_set.remove(s) and studio.users.remove(u)
    if isinstance(instance, Studio):
        studios.append(instance)
    elif isinstance(instance, User):
        for pk in pk_set:
            studios.append(Studio.objects.get(pk=pk))
    for studio in studios:
        if studio.users.count() == 0:
            studio.delete()
            # don't save after delete...'


@receiver(pre_delete, sender=User)
def delete_studio_with_no_user__del(instance, **kwargs):
    studios = instance.studio_set.all()
    for studio in studios:
        # if the studio has only one user left, that means after this deletion,
        # the studio will has no user left
        if studio.users.count() == 1:
            studio.delete()
