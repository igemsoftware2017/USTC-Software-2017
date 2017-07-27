from django.dispatch import receiver
from django.db.models.signals import pre_delete
from biohub.forum.models import Post, Experience


@receiver(pre_delete, sender=Experience)
def hide_attached_posts(instance, **kwargs):
    for post in instance.post_set.all():
        post.hide()


# @receiver(pre_delete, sender=Post)
# def hide_attached_comments(instance, **kwargs):
#     for comment in instance.comments.all():
#         comment.hide()


# @receiver(pre_delete, sender=Studio)
# @receiver(pre_delete, sender=Brick)
# def hide_attached_threads(instance, **kwargs):
#     for thread in instance.thread_set.all():
#         thread.hide()

#   there is no studios anymore
# @receiver(m2m_changed, sender=Studio.users.through)
# def delete_studio_with_no_user__m2m(instance, pk_set, action, **kwargs):
#     # Warning: Because using post_clear signal we can't get pk_set,
#     # which means we don't know what relations have been cleared.
#     # So please don't use something like user.studios_from_user.clear()
#     # That will leave some empty studio.
#     if action != 'post_remove':
#         return
#     studios = []
#     # consider two situations: user.studios_from_user.remove(s) and studio.users.remove(u)
#     if isinstance(instance, Studio):
#         studios.append(instance)
#     elif isinstance(instance, User):
#         for pk in pk_set:
#             studios.append(Studio.objects.get(pk=pk))
#     for studio in studios:
#         if studio.users.count() == 0 and studio.administrator is None:
#             studio.delete()
#             # don't save after delete...'


# @receiver(pre_delete, sender=User)
# def delete_studio_with_no_user__del(instance, **kwargs):
#     studios = []
#     studios += instance.studios_from_user.all()
#     studios += instance.studios_from_admin.all()
#     for studio in studios:
#         # if the studio has only one user left, that means after this deletion,
#         # the studio will has no user left
#         if (studio.users.count() == 1 and studio.administrator is None) or \
#                 (studio.users.count() == 0 and studio.administrator is not None):
#             studio.delete()


# # Waring: if use user.studios_from_admin.remove(studio),
# # please add bulk=False to make sure post_save is sent
# @receiver(post_save, sender=Studio)
# def delete_studio_with_no_user__save(instance, **kwargs):
#     if instance.users.count() == 0 and instance.administrator is None:
#         instance.delete()
