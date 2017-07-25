from biohub.forum.models import Studio, Thread, Post, Comment
from biohub.accounts.models import User
from django.test import TestCase
import random


def create_random_string():
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join([random.choice(seed) for x in range(0, 20)])


def create_new_user(**kwargs):
    user = User(username=create_random_string(), password='123456', **kwargs)
    user.save()
    return user


def create_new_studio(user, **kwargs):
    studio = Studio(name=create_random_string(), administrator=user, **kwargs)
    # save before calling add()!
    # studio.save()
    # studio.users.add(user)
    studio.save()
    return studio


def create_new_thread(author, studio, **kwargs):
    thread = Thread(title='this is a title', author=author, studio=studio, **kwargs)
    thread.save()
    return thread


def create_new_post(thread, author, **kwargs):
    post = Post.objects.create(thread=thread, content=create_random_string(),
                               author=author, **kwargs)
    return post


def create_new_comment(thread, post, author, **kwargs):
    comment = Comment.objects.create(thread=thread, content=create_random_string(),
                                     author=author, reply_to=post, **kwargs)
    return comment


class ThreadModelTests(TestCase):
    def setUp(self):
        self.user = create_new_user()
        self.studio = create_new_studio(self.user)

    def test_delete_a_thread_those_posts_and_comments_should_hide(self):
        thread = create_new_thread(self.user, self.studio)
        post1 = create_new_post(thread, self.user)
        post2 = create_new_post(thread, self.user)
        comment2 = create_new_comment(thread, post2, self.user)
        self.assertIs(post1.is_visible, True)
        self.assertIs(post2.is_visible, True)
        self.assertIs(comment2.is_visible, True)
        thread.delete()
        # remember to reload post1 and post2 and comment2!
        self.assertIs(Post.objects.get(pk=post1.id).is_visible, False)
        self.assertIs(Post.objects.get(pk=post2.id).is_visible, False)
        self.assertIs(Comment.objects.get(pk=comment2.id).is_visible, False)

    def test_hide_and_show_a_thread_and_the_actions_of_those_posts_and_comments(self):
        thread = create_new_thread(self.user, self.studio)
        post2 = create_new_post(thread, self.user)
        comment2 = create_new_comment(thread, post2, self.user)
        self.assertIs(post2.is_visible, True)
        self.assertIs(comment2.is_visible, True)
        thread.hide()
        self.assertIs(Post.objects.get(pk=post2.id).is_visible, False)
        self.assertIs(Comment.objects.get(pk=comment2.id).is_visible, False)
        thread.show()
        self.assertIs(Post.objects.get(pk=post2.id).is_visible, True)
        self.assertIs(Comment.objects.get(pk=comment2.id).is_visible, True)

    def test_delete_thread_queryset_and_posts_and_comments_should_hide(self):
        thread1 = create_new_thread(self.user, self.studio)
        thread2 = create_new_thread(self.user, self.studio)
        post1 = create_new_post(thread1, self.user)
        post2 = create_new_post(thread2, self.user)
        comment2 = create_new_comment(thread2, post2, self.user)
        Thread.objects.all().delete()
        self.assertIs(Post.objects.get(pk=post1.id).is_visible, False)
        self.assertIs(Post.objects.get(pk=post2.id).is_visible, False)
        self.assertIs(Comment.objects.get(pk=comment2.id).is_visible, False)

    def test_getting_posts_directly_attaching_to_thread(self):
        thread = create_new_thread(self.user, self.studio)
        post = create_new_post(thread, self.user)
        create_new_comment(thread, post, self.user)
        thread.get_post_set_by(pk=post.id)
        thread.get_post_set_filter(pk=post.id)
        self.assertEqual(thread.get_post_set_all().count(), 1)
        self.assertEqual(thread.get_post_set_all()[0].id, post.id)


class PostModelTests(TestCase):
    def setUp(self):
        self.user = create_new_user()
        self.studio = create_new_studio(self.user)

    def test_delete_a_post_those_comments_should_hide(self):
        thread = create_new_thread(self.user, self.studio)
        post = create_new_post(thread, self.user)
        comment = create_new_comment(thread, post, self.user)
        self.assertIs(comment.is_visible, True)
        post.delete()
        self.assertIs(Comment.objects.get(pk=comment.id).is_visible, False)

    def test_hide_and_show_a_post_and_the_actions_of_those_comments(self):
        thread = create_new_thread(self.user, self.studio)
        post = create_new_post(thread, self.user)
        comment = create_new_comment(thread, post, self.user)
        self.assertIs(post.is_visible, True)
        self.assertIs(comment.is_visible, True)
        post.hide()
        self.assertIs(Post.objects.get(pk=post.id).is_visible, False)
        self.assertIs(Comment.objects.get(pk=comment.id).is_visible, False)
        post.show()
        self.assertIs(Post.objects.get(pk=post.id).is_visible, True)
        self.assertIs(Comment.objects.get(pk=comment.id).is_visible, True)

    def test_delete_post_queryset_and_comments_should_hide(self):
        thread = create_new_thread(self.user, self.studio)
        post1 = create_new_post(thread, self.user, up_vote_num=10)
        post2 = create_new_post(thread, self.user, up_vote_num=10)
        comment1 = create_new_comment(thread, post1, self.user)
        comment2 = create_new_comment(thread, post2, self.user)
        Post.objects.filter(up_vote_num=10).delete()
        self.assertIs(Comment.objects.get(pk=comment1.id).is_visible, False)
        self.assertIs(Comment.objects.get(pk=comment2.id).is_visible, False)


class CommentModelTests(TestCase):
    def setUp(self):
        self.user = create_new_user()
        self.studio = create_new_studio(self.user)

    def test_delete_a_comment_those_attached_comments_should_hide(self):
        thread = create_new_thread(self.user, self.studio)
        post = create_new_post(thread, self.user)
        comment1 = create_new_comment(thread, post, self.user)
        comment11 = create_new_comment(thread, comment1, self.user)
        comment111 = create_new_comment(thread, comment11, self.user)
        comment12 = create_new_comment(thread, comment1, self.user)
        self.assertIs(comment11.is_visible, True)
        self.assertIs(comment12.is_visible, True)
        self.assertIs(comment111.is_visible, True)
        comment1.delete()
        self.assertIs(Comment.objects.get(pk=comment11.id).is_visible, False)
        self.assertIs(Comment.objects.get(pk=comment12.id).is_visible, False)
        self.assertIs(Comment.objects.get(pk=comment111.id).is_visible, False)

    def test_hide_and_show_a_comment_and_the_action_of_the_attached_comments(self):
        thread = create_new_thread(self.user, self.studio)
        post = create_new_post(thread, self.user)
        comment1 = create_new_comment(thread, post, self.user)
        comment11 = create_new_comment(thread, comment1, self.user)
        comment111 = create_new_comment(thread, comment11, self.user)
        self.assertIs(comment11.is_visible, True)
        self.assertIs(comment111.is_visible, True)
        comment1.hide()
        self.assertIs(Comment.objects.get(pk=comment11.id).is_visible, False)
        self.assertIs(Comment.objects.get(pk=comment111.id).is_visible, False)
        comment1.show()
        self.assertIs(Comment.objects.get(pk=comment11.id).is_visible, True)
        self.assertIs(Comment.objects.get(pk=comment111.id).is_visible, True)

    def test_delete_comment_queryset_and_attached_comments_should_hide(self):
        thread = create_new_thread(self.user, self.studio)
        post = create_new_post(thread, self.user)
        comment1 = create_new_comment(thread, post, self.user, up_vote_num=10)
        comment2 = create_new_comment(thread, post, self.user, up_vote_num=10)
        comment11 = create_new_comment(thread, comment1, self.user)
        comment21 = create_new_comment(thread, comment2, self.user)
        Comment.objects.filter(up_vote_num=10).delete()
        self.assertIs(Comment.objects.get(pk=comment11.id).is_visible, False)
        self.assertIs(Comment.objects.get(pk=comment21.id).is_visible, False)


class StudioModelTests(TestCase):
    def test_delete_studio_and_threads_should_hide(self):
        user = create_new_user()
        studio = create_new_studio(user)
        thread = create_new_thread(user, studio)
        self.assertIs(thread.is_visible, True)
        studio.delete()
        self.assertIs(Thread.objects.get(pk=thread.id).is_visible, False)

    def test_if_all_users_quit_the_studio_should_be_deleted(self):
        user1 = create_new_user()
        studio1 = create_new_studio(user1)
        user2 = create_new_user()
        studio1.users.add(user2)
        studio2 = create_new_studio(user2)
        studio3 = create_new_studio(user2)
        user1.studios_from_admin.remove(studio1)
        user2.studios_from_user.remove(studio1)
        user2.studios_from_admin.remove(studio3, bulk=False)
        Studio.objects.get(pk=studio2.id)
        self.assertRaises(Studio.DoesNotExist, Studio.objects.get, pk=studio1.id)
        self.assertRaises(Studio.DoesNotExist, Studio.objects.get, pk=studio3.id)

    def test_if_studio_kicks_everyone_out_the_studio_should_be_deleted(self):
        user1 = create_new_user()
        studio = create_new_studio(user1)
        user2 = create_new_user()
        studio.users.add(user2)
        studio.users.remove(user2)
        studio.administrator = None
        studio.save()
        self.assertRaises(Studio.DoesNotExist, Studio.objects.get, pk=studio.id)

    def test_if_all_user_deleted_the_studio_should_be_deleted(self):
        user1 = create_new_user()
        user2 = create_new_user()
        studio = create_new_studio(user1)
        studio.users.add(user2)
        user1.delete()
        user2.delete()
        self.assertRaises(Studio.DoesNotExist, Studio.objects.get, pk=studio.id)

    # def test_if_a_user_clear_all_his_studio_and_cause_a_studio_to_have_no_member_that_should_be_deleted(self):
    #     user1 = create_new_user()
    #     studio = create_new_studio(user1)
    #     user2 = create_new_user()
    #     studio.users.add(user2)
    #     user2.studio_set.clear()
    #     self.assertEqual(studio.users.count(), 1)
    #     user1.studio_set.clear()
    #     self.assertRaises(Studio.DoesNotExist, Studio.objects.get, pk=studio.id)

    def test_delete_user_the_relation_will_be_deleted_at_the_same_time(self):
        user1 = create_new_user()
        studio = create_new_studio(user1)
        user2 = create_new_user()
        studio.users.add(user2)
        user1.delete()
        self.assertEqual(studio.users.count(), 1)
        self.assertRaises(User.DoesNotExist, studio.users.get, pk=user1.id)

    def test_delete_studio_the_relation_will_be_deleted_at_the_same_time(self):
        user = create_new_user()
        studio = create_new_studio(user)
        studio.delete()
        self.assertEqual(user.studios_from_admin.count(), 0)
        self.assertRaises(Studio.DoesNotExist, user.studios_from_admin.get, pk=studio.id)
