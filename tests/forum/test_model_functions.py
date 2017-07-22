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
    studio.save()
    studio.users.add(user)
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


class ThreadModelTests(TestCase):
    def set_up(self):
        self.user = create_new_user()
        self.studio = create_new_studio(self.user)

    def test_delete_a_thread_those_posts_and_comments_should_hide(self):
        self.set_up()
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
        self.set_up()
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


class PostModelTests(TestCase):
    def set_up(self):
        self.user = create_new_user()
        self.studio = create_new_studio(self.user)

    def test_delete_a_post_those_comments_should_hide(self):
        self.set_up()
        thread = create_new_thread(self.user, self.studio)
        post = create_new_post(thread, self.user)
        comment = create_new_comment(thread, post, self.user)
        self.assertIs(comment.is_visible, True)
        post.delete()
        self.assertIs(Comment.objects.get(pk=comment.id).is_visible, False)

    def test_hide_and_show_a_post_and_the_actions_of_those_comments(self):
        self.set_up()
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


class CommentModelTests(TestCase):
    def set_up(self):
        self.user = create_new_user()
        self.studio = create_new_studio(self.user)

    def test_delete_a_comment_those_attached_comments_should_hide(self):
        self.set_up()
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
        self.set_up()
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
