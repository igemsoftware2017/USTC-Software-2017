from django.db.models import Q, Subquery
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from biohub.notices.tool import Dispatcher
from biohub.notices.models import Notice

from biohub.forum.models import Post, Experience
from biohub.forum.models import Activity
from biohub.forum.user_defined_signals import voted_experience_signal, \
    rating_brick_signal, watching_brick_signal, unwatching_brick_signal,\
    unvoted_experience_signal

from biohub.biobrick.models import Biobrick


@receiver(pre_delete, sender=Experience)
def remove_experience_related_objects(instance, **kwargs):

    if instance.content:
        instance.content.delete()

    condition = Q(experience=instance) | Q(post__pk__in=Subquery(instance.posts.values('id')))

    Activity.objects.filter(condition).delete()

    Notice.objects.filter(condition).delete()


forum_dispatcher = Dispatcher('Forum')


@receiver(pre_delete, sender=Post)
def remove_post_activity_and_notices(instance, **kwargs):

    Activity.objects.filter(post=instance).delete()
    Notice.objects.filter(post=instance).delete()


@receiver(post_save, sender=Post)
def send_notice_to_the_experience_author_on_commenting(instance, created, **kwargs):
    if created:
        # only send a notice when the post is created for the first time.
        # the later modifications of the posts won't cause sending a notice.
        experience = instance.experience
        author = experience.author
        # ignore if the comment's author is the same as the experience author
        if not author or author.id == instance.author.id:
            return
        forum_dispatcher.send_or_update(
            author,
            '{{post.author.username|url:post.author}} commented '
            'your experience {{ experience.title|url:experience }} '
            'at brick {{experience.brick.part_name|url:experience.brick}}.',
            post=instance,
            experience=experience,
            target=instance,
            target_slug='comment experience',
            actor=instance.author,
            filter_fields=('actor', 'target_slug', 'user', 'category')
        )


@receiver(post_save, sender=Post)
def add_creating_post_activity(instance, created, **kwargs):

    exp_author = instance.experience.author

    if not exp_author:
        return False

    Activity.objects.create_activity(
        type='Comment', user=instance.author, target=instance,
        brick_name=instance.experience.brick.part_name,
        params={
            'partName': instance.experience.brick.part_name,
            'expId': instance.experience.id,
            'postId': instance.id,
            'expTitle': instance.experience.title
        }
    )


@receiver(post_save, sender=Experience)
def add_creating_experience_activity(instance, created, **kwargs):
    # do nothing when it's from iGEM's website
    if instance.author:
        if created:
            Activity.objects.create_activity(
                type='Experience', user=instance.author, target=instance,
                brick_name=instance.brick.part_name,
                params={
                    'partName': instance.brick.part_name,
                    'expId': instance.id,
                    'expTitle': instance.title
                }
            )


@receiver(rating_brick_signal, sender=Biobrick)
def add_rating_brick_activity(instance, rating_score, user_rating, **kwargs):
    Activity.objects.create_activity(
        type='Rating', user=user_rating,
        brick_name=instance.part_name,
        params={
            'score': str(rating_score),  # make sure `rating_score` is JSON-serializable
            'partName': instance.part_name,
        }
    )


@receiver(watching_brick_signal, sender=Biobrick)
def add_watching_brick_activity(instance, user, **kwargs):
    Activity.objects.create_activity(
        type='Watch', user=user,
        brick_name=instance.part_name,
        params={
            'partName': instance.part_name,
            'intro': instance.short_desc
        }
    )


@receiver(unwatching_brick_signal, sender=Biobrick)
def remove_watching_brick_activity(instance, user, **kwargs):
    Activity.objects.filter(
        type='Watch',
        user=user, brick_name=instance.part_name
    ).delete()


@receiver(voted_experience_signal, sender=Experience)
def send_notice_to_experience_author_on_voting(
        instance, user_voted,
        current_votes, **kwargs):
    author = instance.author
    # ignore if voting an experience fetched from iGEM website.
    if author is None:
        return
    brick = instance.brick
    forum_dispatcher.send(
        author,
        '{{actor.username|url:actor}}'
        ' voted your experience '
        '{{ experience.title|url:experience }}'
        ' at brick {{brick.part_name|url:brick}}. '
        'Now you have {{current_votes}} vote(s) for that experience.',
        experience=instance,
        brick=brick,
        current_votes=current_votes,
        target=instance,
        target_slug='vote_experience',
        actor=user_voted
    )


@receiver(voted_experience_signal, sender=Experience)
def add_voted_experience_activity(instance, user_voted, **kwargs):
    Activity.objects.create_activity(
        type='Star', user=user_voted,
        brick_name=instance.brick.part_name,
        target=instance,
        params={
            'partName': instance.brick.part_name,
            'expId': instance.id,
            'expTitle': instance.title
        }
    )


@receiver(unvoted_experience_signal, sender=Experience)
def remove_voted_experience_activity(instance, user_unvoted, **kwargs):

    Activity.objects.filter(
        experience=instance, type='Star', user=user_unvoted).delete()
    Notice.objects.filter(
        experience=instance, target_slug='vote_experience',
        actor=user_unvoted
    ).delete()
