from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from rest_framework.reverse import reverse

from biohub.forum.models import Post, Experience
from biohub.forum.user_defined_signals import rating_experience_signal, \
    up_voting_post_signal
from biohub.notices.tool import Dispatcher


@receiver(pre_delete, sender=Experience)
def hide_attached_posts(instance, **kwargs):
    for post in instance.post_set.all():
        post.hide()

forum_dispatcher = Dispatcher('Forum')


@receiver(post_save, sender=Post)
def send_notice_to_the_experience_author_on_commenting(instance, created, **kwargs):
    if created:
        # only send a notice when the post is created for the first time.
        # the later modifications of the posts won't cause sending a notice.
        experience = instance.experience
        author = experience.author
        # ignore if the comment's author is the same as the experience author
        if author == instance.author:
            return
        experience_url = reverse('api:forum:experience-detail', kwargs={'pk': experience.id})
        post_author_url = instance.author.api_url
        brick_url = reverse('api:forum:brick-detail', kwargs={'pk': experience.brick.id})
        forum_dispatcher.send(author, '{{instance.author.username|url:post_author_url}} commented on '
                                      'your experience (Title: {{ experience.title|url:experience_url }})'
                                      ' of brick BBA_{{experience.brick.name|url:brick_url}}.',
                              instance=instance, experience=experience, brick_url=brick_url,
                              post_author_url=post_author_url, experience_url=experience_url)


@receiver(rating_experience_signal, sender=Experience)
def send_notice_to_the_experience_author_on_rating(instance, rating_score,
                                                   curr_score, user_rating, **kwargs):
    author = instance.author
    brick_url = reverse('api:forum:brick-detail', kwargs={'pk': instance.brick.id})
    experience_url = reverse('api:forum:experience-detail', kwargs={'pk': instance.id})
    user_rating_url = user_rating.api_url
    forum_dispatcher.send(author, '{{user_rating.username|url:user_rating_url}} rated {{rating_score}} '
                                  'on your experience (Title: {{ experience.title|url:experience_url }})'
                                  ' of brick BBA_{{experience.brick.name|url:brick_url}}. Now the '
                                  'score of the experience is {{curr_score}}.',
                          experience=instance, brick_url=brick_url, experience_url=experience_url,
                          user_rating=user_rating, user_rating_url=user_rating_url,
                          rating_score=rating_score, curr_score=curr_score)


@receiver(up_voting_post_signal, sender=Post)
def send_notice_to_post_author_on_up_voting(instance, user_up_voting,
                                            curr_up_vote_num, **kwargs):
    author = instance.author
    experience = instance.experience
    brick = instance.experience.brick
    experience_url = reverse('api:forum:experience-detail', kwargs={'pk': experience.id})
    brick_url = reverse('api:forum:brick-detail', kwargs={'pk': brick.id})
    user_up_voting_url = user_up_voting.api_url
    post_url = reverse('api:forum:post-detail', kwargs={'pk': instance.id})
    forum_dispatcher.send(author, '{{user_up_voting.username|url:user_up_voting_url}}'
                                  ' voted for {{"your post"|url:post_url}} on experience '
                                  '(Title: {{ experience.title|url:experience_url }})'
                                  ' of brick BBA_{{brick.name|url:brick_url}}. '
                                  'Now you have {{curr_up_vote_num}} vote(s) for that post.',
                          experience=experience, brick_url=brick_url, experience_url=experience_url,
                          user_up_voting=user_up_voting, user_up_voting_url=user_up_voting_url,
                          brick=brick, curr_up_vote_num=curr_up_vote_num, post_url=post_url)


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
