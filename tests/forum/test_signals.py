from biohub.forum.models import Post, Experience, Article
from biohub.biobrick.models import Biobrick, BiobrickMeta
from biohub.accounts.models import User
from django.test import TestCase
import random


def create_random_string():
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join([random.choice(seed) for x in range(0, 7)])


def create_new_user(**kwargs):
    user = User.objects.create_test_user(username=create_random_string(), **kwargs)
    user.set_password('123456')
    user.save()
    return user


def create_new_article(**kwargs):
    article = Article.objects.create(text=create_random_string(), **kwargs)
    return article


def create_new_experience(author, **kwargs):
    brick = None
    if 'brick' in kwargs:
        brick = kwargs.pop('brick')
    else:
        brick = create_new_brick()
    experience = Experience(title='this is a title', author=author, brick=brick,
                            content=create_new_article(), **kwargs)
    experience.save()
    return experience


def create_new_brick(**kwargs):
    brick = BiobrickMeta.objects.create(
        part_name=create_random_string(), document=create_new_article(),
        **kwargs
    )
    return brick


def create_new_post(experience, author, **kwargs):
    post = Post.objects.create(experience=experience, content=create_random_string(),
                               author=author, **kwargs)
    return post


class ExperienceSignalTests(TestCase):

    def setUp(self):
        self.user = create_new_user()
        self.experience = create_new_experience(author=self.user)
        self.experience2 = create_new_experience(author=self.user)

    def test_delete_a_experience_those_posts_should_delete(self):
        experience = create_new_experience(author=self.user)
        post1 = create_new_post(experience=experience, author=self.user)
        post2 = create_new_post(experience, self.user)
        self.assertTrue(post1.is_visible)
        self.assertTrue(post2.is_visible)
        experience.delete()
        self.assertFalse(Post.objects.count(), 0)

    def test_delete_experience_queryset_and_posts_should_delete(self):
        experience1 = create_new_experience(self.user)
        experience2 = create_new_experience(self.user)
        post1 = create_new_post(experience1, self.user)  # noqa
        post2 = create_new_post(experience2, self.user)  # noqa
        Experience.objects.all().delete()
        self.assertFalse(Post.objects.count(), 0)

    def delete_experience_the_article_should_be_deleted(self):
        article_id = self.experience.content.id
        Article.objects.get(pk=article_id)
        self.experience.delete()
        self.assertRaises(Article.DoesNotExist, Article.objects.get, {
            'pk': article_id
        })

    def delete_queryset_all_the_articles_attached_should_be_deleted(self):
        article_id = self.experience.content.id
        Article.objects.get(pk=article_id)
        article_id2 = self.experience2.content.id
        Article.objects.get(pk=article_id2)
        BiobrickMeta.objects.all().delete()
        self.assertRaises(Article.DoesNotExist, Article.objects.get, {
            'pk': article_id
        })
        self.assertRaises(Article.DoesNotExist, Article.objects.get, {
            'pk': article_id2
        })


class BrickSignalTests(TestCase):

    def setUp(self):
        self.brick = create_new_brick()
        self.brick2 = create_new_brick()

    def delete_brick_the_article_should_be_deleted(self):
        article_id = self.brick.document.id
        Article.objects.get(pk=article_id)
        self.brick.delete()
        self.assertRaises(Article.DoesNotExist, Article.objects.get, {
            'pk': article_id
        })

    def delete_queryset_all_the_articles_attached_should_be_deleted(self):
        article_id = self.brick.document.id
        Article.objects.get(pk=article_id)
        article_id2 = self.brick2.document.id
        Article.objects.get(pk=article_id2)
        BiobrickMeta.objects.all().delete()
        self.assertRaises(Article.DoesNotExist, Article.objects.get, {
            'pk': article_id
        })
        self.assertRaises(Article.DoesNotExist, Article.objects.get, {
            'pk': article_id2
        })


class PostSignalTests(TestCase):

    def setUp(self):
        self.user1 = create_new_user()
        self.user2 = create_new_user()
        self.brick = BiobrickMeta.objects.create(part_name='BBa_K314110')
        self.experience1 = create_new_experience(self.user1, brick=self.brick)
        self.post1 = create_new_post(self.experience1, self.user1)
        self.post2 = create_new_post(self.experience1, self.user2)

    def test_creating_a_new_post_will_notice_the_author_of_the_experience(self):
        self.assertEqual(self.user1.notices.all().count(), 1)

    def test_modifying_a_new_post_will_not_notice(self):
        self.post2.content = 'WTF'
        self.post2.save()
        self.assertEqual(self.user1.notices.all().count(), 1)


class UpVotingSignalTests(TestCase):

    def setUp(self):
        self.user1 = create_new_user()
        self.user2 = create_new_user()
        self.brick = BiobrickMeta.objects.create(part_name='BBa_K314110')
        self.experience1 = create_new_experience(self.user1, brick=self.brick)
        self.post1 = create_new_post(self.experience1, self.user1)

    def test_up_vote(self):
        self.assertTrue(self.experience1.vote(self.user2))
        self.assertEqual(self.user1.notices.all().count(), 1)


class WatchSigalTests(TestCase):

    def setUp(self):
        self.brick = Biobrick.objects.get(part_name='BBa_K314110')
        self.user = create_new_user()

    def test_watch_the_brick_and_receive_notice(self):
        self.assertIs(self.brick.watch(self.user), True)
        user2 = create_new_user()
        # publishing own experience won't receive notice
        create_new_experience(self.user, brick=self.brick.meta_instance)
        self.assertEqual(self.user.notices.all().count(), 0)
        create_new_experience(user2, brick=self.brick.meta_instance)
        self.assertEqual(self.user.notices.all().count(), 1)
