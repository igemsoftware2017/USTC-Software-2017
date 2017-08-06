from biohub.forum.models import Post, Experience, Article, Brick
from biohub.accounts.models import User
from django.test import TestCase
import random


def create_random_string():
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join([random.choice(seed) for x in range(0, 20)])


def create_new_user(**kwargs):
    user = User.objects.create(username=create_random_string(), **kwargs)
    user.set_password('123456')
    user.save()
    return user


def create_new_article(**kwargs):
    article = Article.objects.create(text=create_random_string(), **kwargs)
    return article


def create_new_experience(author, **kwargs):
    experience = Experience(title='this is a title', author=author,
                        content=create_new_article(), **kwargs)
    experience.save()
    return experience


def create_new_brick(**kwargs):
    brick = Brick(name=create_random_string(), document=create_new_article(),
                  **kwargs)
    return brick


def create_new_post(experience, author, **kwargs):
    post = Post.objects.create(experience=experience, content=create_random_string(),
                               author=author, **kwargs)
    return post


# def create_new_comment(thread, post, author, **kwargs):
#     comment = Comment.objects.create(thread=thread, content=create_random_string(),
#                                      author=author, reply_to=post, **kwargs)
#     return comment


class ExperienceSignalTests(TestCase):
    def setUp(self):
        self.user = create_new_user()
        self.experience = create_new_experience(author=self.user)
        self.experience2 = create_new_experience(author=self.user)

    def test_delete_a_experience_those_posts_should_hide(self):
        experience = create_new_experience(author=self.user)
        post1 = create_new_post(experience=experience, author=self.user)
        post2 = create_new_post(experience, self.user)
        self.assertIs(post1.is_visible, True)
        self.assertIs(post2.is_visible, True)
        experience.delete()
        # remember to reload post1 and post2 and comment2!
        self.assertIs(Post.objects.get(pk=post1.id).is_visible, False)
        self.assertIs(Post.objects.get(pk=post2.id).is_visible, False)
    #
    # def test_hide_and_show_a_thread_and_the_actions_of_those_posts_and_comments(self):
    #     thread = create_new_thread(self.user, self.studio)
    #     post2 = create_new_post(thread, self.user)
    #     comment2 = create_new_comment(thread, post2, self.user)
    #     self.assertIs(post2.is_visible, True)
    #     self.assertIs(comment2.is_visible, True)
    #     thread.hide()
    #     self.assertIs(Post.objects.get(pk=post2.id).is_visible, False)
    #     self.assertIs(Comment.objects.get(pk=comment2.id).is_visible, False)
    #     thread.show()
    #     self.assertIs(Post.objects.get(pk=post2.id).is_visible, True)
    #     self.assertIs(Comment.objects.get(pk=comment2.id).is_visible, True)

    def test_delete_experience_queryset_and_posts_should_hide(self):
        experience1 = create_new_experience(self.user)
        experience2 = create_new_experience(self.user)
        post1 = create_new_post(experience1, self.user)
        post2 = create_new_post(experience2, self.user)
        Experience.objects.all().delete()
        self.assertIs(Post.objects.get(pk=post1.id).is_visible, False)
        self.assertIs(Post.objects.get(pk=post2.id).is_visible, False)

    # def test_getting_posts_directly_attaching_to_thread(self):
    #     thread = create_new_thread(self.user, self.studio)
    #     post = create_new_post(thread, self.user)
    #     create_new_comment(thread, post, self.user)
    #     thread.get_post_set_by(pk=post.id)
    #     thread.get_post_set_filter(pk=post.id)
    #     self.assertEqual(thread.get_post_set_all().count(), 1)
    #     self.assertEqual(thread.get_post_set_all()[0].id, post.id)

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
        Brick.objects.all().delete()
        self.assertRaises(Article.DoesNotExist, Article.objects.get, {
            'pk': article_id
        })
        self.assertRaises(Article.DoesNotExist, Article.objects.get, {
            'pk': article_id2
        })


# class PostModelTests(TestCase):
#     def setUp(self):
#         self.user = create_new_user()
#         self.studio = create_new_studio(self.user)
#
#     def test_delete_a_post_those_comments_should_hide(self):
#         thread = create_new_thread(self.user, self.studio)
#         post = create_new_post(thread, self.user)
#         comment = create_new_comment(thread, post, self.user)
#         self.assertIs(comment.is_visible, True)
#         post.delete()
#         self.assertIs(Comment.objects.get(pk=comment.id).is_visible, False)
#
#     def test_hide_and_show_a_post_and_the_actions_of_those_comments(self):
#         thread = create_new_thread(self.user, self.studio)
#         post = create_new_post(thread, self.user)
#         comment = create_new_comment(thread, post, self.user)
#         self.assertIs(post.is_visible, True)
#         self.assertIs(comment.is_visible, True)
#         post.hide()
#         self.assertIs(Post.objects.get(pk=post.id).is_visible, False)
#         self.assertIs(Comment.objects.get(pk=comment.id).is_visible, False)
#         post.show()
#         self.assertIs(Post.objects.get(pk=post.id).is_visible, True)
#         self.assertIs(Comment.objects.get(pk=comment.id).is_visible, True)
#
#     def test_delete_post_queryset_and_comments_should_hide(self):
#         thread = create_new_thread(self.user, self.studio)
#         post1 = create_new_post(thread, self.user, up_vote_num=10)
#         post2 = create_new_post(thread, self.user, up_vote_num=10)
#         comment1 = create_new_comment(thread, post1, self.user)
#         comment2 = create_new_comment(thread, post2, self.user)
#         Post.objects.filter(up_vote_num=10).delete()
#         self.assertIs(Comment.objects.get(pk=comment1.id).is_visible, False)
#         self.assertIs(Comment.objects.get(pk=comment2.id).is_visible, False)

#
# class CommentModelTests(TestCase):
#     def setUp(self):
#         self.user = create_new_user()
#         self.studio = create_new_studio(self.user)
#
#     def test_delete_a_comment_those_attached_comments_should_hide(self):
#         thread = create_new_thread(self.user, self.studio)
#         post = create_new_post(thread, self.user)
#         comment1 = create_new_comment(thread, post, self.user)
#         comment11 = create_new_comment(thread, comment1, self.user)
#         comment111 = create_new_comment(thread, comment11, self.user)
#         comment12 = create_new_comment(thread, comment1, self.user)
#         self.assertIs(comment11.is_visible, True)
#         self.assertIs(comment12.is_visible, True)
#         self.assertIs(comment111.is_visible, True)
#         comment1.delete()
#         self.assertIs(Comment.objects.get(pk=comment11.id).is_visible, False)
#         self.assertIs(Comment.objects.get(pk=comment12.id).is_visible, False)
#         self.assertIs(Comment.objects.get(pk=comment111.id).is_visible, False)
#
#     def test_hide_and_show_a_comment_and_the_action_of_the_attached_comments(self):
#         thread = create_new_thread(self.user, self.studio)
#         post = create_new_post(thread, self.user)
#         comment1 = create_new_comment(thread, post, self.user)
#         comment11 = create_new_comment(thread, comment1, self.user)
#         comment111 = create_new_comment(thread, comment11, self.user)
#         self.assertIs(comment11.is_visible, True)
#         self.assertIs(comment111.is_visible, True)
#         comment1.hide()
#         self.assertIs(Comment.objects.get(pk=comment11.id).is_visible, False)
#         self.assertIs(Comment.objects.get(pk=comment111.id).is_visible, False)
#         comment1.show()
#         self.assertIs(Comment.objects.get(pk=comment11.id).is_visible, True)
#         self.assertIs(Comment.objects.get(pk=comment111.id).is_visible, True)
#
#     def test_delete_comment_queryset_and_attached_comments_should_hide(self):
#         thread = create_new_thread(self.user, self.studio)
#         post = create_new_post(thread, self.user)
#         comment1 = create_new_comment(thread, post, self.user, up_vote_num=10)
#         comment2 = create_new_comment(thread, post, self.user, up_vote_num=10)
#         comment11 = create_new_comment(thread, comment1, self.user)
#         comment21 = create_new_comment(thread, comment2, self.user)
#         Comment.objects.filter(up_vote_num=10).delete()
#         self.assertIs(Comment.objects.get(pk=comment11.id).is_visible, False)
#         self.assertIs(Comment.objects.get(pk=comment21.id).is_visible, False)


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
        Brick.objects.all().delete()
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
        self.brick = Brick.objects.create(name='K314110')
        self.experience1 = create_new_experience(self.user1, brick=self.brick)
        self.post1 = create_new_post(self.experience1, self.user1)
        self.post2 = create_new_post(self.experience1, self.user2)

    def test_creating_a_new_post_will_notice_the_author_of_the_experience(self):
        self.assertEqual(self.user1.notices.all().count(), 1)

    def test_modifying_a_new_post_will_not_notice(self):
        self.post2.content = 'WTF'
        self.post2.save()
        self.assertEqual(self.user1.notices.all().count(), 1)
