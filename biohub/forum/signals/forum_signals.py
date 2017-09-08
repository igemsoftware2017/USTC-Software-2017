from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from rest_framework.reverse import reverse

from biohub.forum.models import Post, Experience, Brick
from biohub.forum.models import Activity, ActivityParam
from biohub.forum.user_defined_signals import up_voting_experience_signal, rating_brick_signal, watching_brick_signal
from biohub.notices.tool import Dispatcher


@receiver(pre_delete, sender=Experience)
def hide_attached_posts(instance, **kwargs):
    instance.post_set.update(is_visible=False)


forum_dispatcher = Dispatcher('Forum')


@receiver(post_save, sender=Post)
def send_notice_to_the_experience_author_on_commenting(instance, created, **kwargs):
    if created:
        # only send a notice when the post is created for the first time.
        # the later modifications of the posts won't cause sending a notice.
        experience = instance.experience
        author = experience.author
        # ignore if the comment's author is the same as the experience author
        if author.id == instance.author.id:
            return
        experience_url = reverse(
            'api:forum:experience-detail', kwargs={'pk': experience.id}
        )
        post_author_url = instance.author.api_url
        brick_url = reverse(
            'api:forum:brick-detail',
            kwargs={'pk': experience.brick.id}
        )
        forum_dispatcher.send(
            author,
            '{{instance.author.username|url:post_author_url}} commented on '
            'your experience (Title: {{ experience.title|url:experience_url }})'
            ' of brick BBA_{{experience.brick.name|url:brick_url}}.',
            instance=instance, experience=experience, brick_url=brick_url,
            post_author_url=post_author_url, experience_url=experience_url
        )


@receiver(post_save, sender=Experience)
def add_creating_experience_activity(instance, created, **kwargs):
    # do nothing when it's from iGEM's website
    if instance.author:
        if created:
            activityparam = ActivityParam.objects.create(
                type='Experience', user=instance.author,
                partName=instance.brick.name, expLink=reverse(
                    'api:forum:experience-detail', kwargs={'pk': instance.id}
                )
            )
            Activity.objects.create(
                type='Experience', user=instance.author, params=activityparam)


@receiver(post_save, sender=Post)
def add_creating_post_activity(instance, created, **kwargs):
    activityparam = ActivityParam.objects.create(
        type='Comment', user=instance.author, partName=instance.experience.brick.name,
        expLink=reverse('api:forum:experience-detail', kwargs={'pk': instance.experience.id})
    )
    Activity.objects.create(
        type='Comment', user=instance.author, params=activityparam)


@receiver(up_voting_experience_signal, sender=Experience)
def add_up_voting_experience_activity(instance, user_up_voting, **kwargs):
    activityparam = ActivityParam.objects.create(
        type='Star', user=user_up_voting, partName=instance.brick.name, expLink=reverse(
            'api:forum:experience-detail', kwargs={'pk': instance.id}
        )
    )
    Activity.objects.create(
        type='Star', user=user_up_voting, params=activityparam
    )


@receiver(rating_brick_signal, sender=Brick)
def add_rating_brick_activity(instance, rating_score, user_rating, **kwargs):
    activityparam = ActivityParam(type='Rating', user=user_rating, expLink=reverse(
        'api:forum:brick-detail', kwargs={'pk': instance.id}), score=rating_score, partName=instance.name)
    activityparam.save()
    Activity.objects.create(type='Rating', user=user_rating, params=activityparam)


@receiver(watching_brick_signal, sender=Brick)
def add_watching_brick_activity(instance, user, **kwargs):
    activityparam = ActivityParam.objects.create(
        type='Watch', user=user, partName=instance.name)
    Activity.objects.create(type='Watch', user=user, params=activityparam)


@receiver(up_voting_experience_signal, sender=Experience)
def send_notice_to_experience_author_on_up_voting(instance, user_up_voting,
                                                  curr_up_vote_num, **kwargs):
    author = instance.author
    # ignore if up_voting an experience fetched from iGEM website.
    if author is None:
        return
    brick = instance.brick
    experience_url = reverse(
        'api:forum:experience-detail', kwargs={'pk': instance.id})
    brick_url = reverse('api:forum:brick-detail', kwargs={'pk': brick.id})
    user_up_voting_url = user_up_voting.api_url
    forum_dispatcher.send(
        author,
        '{{user_up_voting.username|url:user_up_voting_url}}'
        ' voted for your experience '
        '(Title: {{ experience.title|url:experience_url }})'
        ' of brick BBA_{{brick.name|url:brick_url}}. '
        'Now you have {{curr_up_vote_num}} vote(s) for that experience.',
        experience=instance, brick_url=brick_url, experience_url=experience_url,
        user_up_voting=user_up_voting, user_up_voting_url=user_up_voting_url,
        brick=brick, curr_up_vote_num=curr_up_vote_num
    )
