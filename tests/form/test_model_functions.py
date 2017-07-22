from biohub.forum.models import Studio, Thread, Post, Comment
from biohub.accounts.models import User
from django.test import TestCase
import random


def create_random_string():
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join([random.choice(seed) for x in range(0, 20)])


def create_new_user():
    user = User(username=create_random_string(), password='123456')
    user.save()
    return user


def create_new_studio(user):
    studio = Studio(name=create_random_string())
    studio.user.add(user)
    studio.save()
    return studio


def create_new_thread(author, studio):
    thread = Thread(title='this is a title', author=author, studio=studio)
    thread.save()
    return thread


def create_new_post(thread, author):
    post = Post(thread=thread, content=create_random_string(), author=author)
    post.save()
    return post


def create_new_comment(thread, post, author):
    comment = Comment(thread=thread, content=create_random_string(), author=author, post=post)
    comment.save()
    return comment

# create an user and his studio for all the tests below
user = create_new_user()
studio = create_new_studio(user)


class ThreadModelTests(TestCase):
    def test_delete_a_thread_those_posts_and_comments_should_hide(self):
        thread = create_new_thread(user, studio)
        post1 = create_new_post(thread, user)
        post2 = create_new_post(thread, user)
        comment2 = create_new_comment(thread, post2, user)
        self.assertIs(post1.is_visible, True)
        self.assertIs(post2.is_visible, True)
        self.assertIs(comment2.is_visible, True)
        thread.delete()
        self.assertIs(post1.is_visible, False)
        self.assertIs(post2.is_visible, False)
        self.assertIs(comment2.is_visible, False)

    def test_hide_and_show_a_thread_and_the_actions_of_those_posts_and_comments(self):
        thread = create_new_thread(user, studio)
        post2 = create_new_post(thread, user)
        comment2 = create_new_comment(thread, post2, user)
        self.assertIs(post2.is_visible, True)
        self.assertIs(comment2.is_visible, True)
        thread.hide()
        self.assertIs(post2.is_visible, False)
        self.assertIs(comment2.is_visible, False)
        thread.show()
        self.assertIs(post2.is_visible, True)
        self.assertIs(comment2.is_visible, True)


class PostModelTests(TestCase):
    def test_delete_a_post_those_comments_should_hide(self):
        thread = create_new_thread(user, studio)
        post = create_new_post(thread, user)
        comment = create_new_comment(thread, post, user)
        self.assertIs(comment.is_visible, True)
        post.delete()
        self.assertIs(comment.is_visible, False)

    def test_hide_and_show_a_post_and_the_actions_of_those_comments(self):
        thread = create_new_thread(user, studio)
        post = create_new_post(thread, user)
        comment = create_new_comment(thread, post, user)
        self.assertIs(post.is_visible, True)
        self.assertIs(comment.is_visible, True)
        post.hide()
        self.assertIs(post.is_visible, False)
        self.assertIs(comment.is_visible, False)
        thread.show()
        self.assertIs(post.is_visible, True)
        self.assertIs(comment.is_visible, True)


class CommentModelTests(TestCase):
    def test_delete_a_comment_those_attached_comments_should_hide(self):
        thread = create_new_thread(user, studio)
        post = create_new_post(thread, user)
        comment1 = create_new_comment(thread, post, user)
        comment11 = create_new_comment(thread, comment1, user)
        comment111 = create_new_comment(thread, comment11, user)
        comment12 = create_new_comment(thread, comment1, user)
        self.assertIs(comment11.is_visible, True)
        self.assertIs(comment12.is_visible, True)
        self.assertIs(comment111.is_visible, True)
        comment1.delete()
        self.assertIs(comment11.is_visible, False)
        self.assertIs(comment12.is_visible, False)
        self.assertIs(comment111.is_visible, False)

    def test_hide_and_show_a_comment_and_the_action_of_the_attached_comments(self):
        thread = create_new_thread(user, studio)
        post = create_new_post(thread, user)
        comment1 = create_new_comment(thread, post, user)
        comment11 = create_new_comment(thread, comment1, user)
        comment111 = create_new_comment(thread, comment11, user)
        self.assertIs(comment11.is_visible, True)
        self.assertIs(comment111.is_visible, True)
        comment1.hide()
        self.assertIs(comment11.is_visible, False)
        self.assertIs(comment111.is_visible, False)
        comment1.show()
        self.assertIs(comment11.is_visible, True)
        self.assertIs(comment111.is_visible, True)
