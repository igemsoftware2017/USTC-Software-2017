from rest_framework.test import APIClient, APITestCase
from unittest import SkipTest  # noqa

from biohub.accounts.models import User
from biohub.notices.models import Notice
from biohub.forum.models import Activity, Experience, Post
from biohub.biobrick.models import Biobrick


class ActivityTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_test_user(username='abc')
        self.user.set_password('123456000+')
        self.another_user = User.objects.create_test_user(username='another')
        self.another_user.set_password('hahaha')
        self.another_user.save()
        self.user.save()

    def test_timeline_permission(self):

        self.assertEqual(
            self.client.get('/api/forum/activities/timeline/').status_code,
            403
        )

    def test_timeline(self):

        self.user.follow(self.another_user)

        brick = Biobrick.objects.get(part_name='BBa_B0032')
        meta = brick.ensure_meta_exists(fetch=True)
        Experience.objects.create(brick=meta, author=self.another_user)
        self.assertTrue(brick.watch(self.another_user))
        self.assertTrue(brick.rate(self.another_user, 2.3))
        brick.refresh_from_db()

        user3 = User.objects.create_test_user('usr3')
        brick2 = Biobrick.objects.get(part_name='BBa_B0015')
        brick2.ensure_meta_exists(fetch=True)
        brick2.watch(user3)
        brick2.watch(self.user)
        brick2.refresh_from_db()

        self.client.force_authenticate(self.user)
        data = self.client.get('/api/forum/activities/timeline/').data

        self.assertEqual(len(data['results']), 4)
        results = data['results']
        self.assertDictContainsSubset({
            'type': 'Watch',
        }, results[0])
        self.assertDictContainsSubset({
            'intro': brick2.short_desc,
            'user': user3.username
        }, results[0]['params'])
        self.assertDictContainsSubset({
            'type': 'Rating',
        }, results[1])
        self.assertDictContainsSubset({
            'type': 'Watch'
        }, results[2])
        self.assertDictContainsSubset({
            'intro': brick.short_desc,
            'score': brick.rate_score,
            'user': self.another_user.username
        }, results[2]['params'])
        self.assertDictContainsSubset({
            'type': 'Experience'
        }, results[3])

    def test_aggregation(self):
        brick, meta, exp = self._simulate()
        Experience.objects.create(brick=meta, author=self.user)
        brick2 = Biobrick.objects.get(part_name='BBa_B0015')
        brick2.ensure_meta_exists(fetch=True)
        brick.star(self.user)
        brick2.star(self.user)

        self.client.force_authenticate(self.user)
        self.assertEqual(
            self.client.get('/api/users/me/stat/').data,
            {'follower_count': 0, 'following_count': 0, 'star_count': 2, 'experience_count': 2}
        )

    def test_simulation(self):
        # raise SkipTest

        client = APIClient()
        response = client.login(username='abc', password='123456000+')

        # fetch some bricks and experiences
        response = client.get('/api/forum/bricks/BBa_B0032/')
        data = response.data
        # publish an experience
        payload = {
            'brick_name': data['part_name'],
            'title': 'title',
            'content_input': {
                'text': 'this is a sample text',
                'file_ids': []
            }
        }
        response = client.post('/api/forum/experiences/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        exp_id = response.data['id']
        # rate a brick
        response = client.post('/api/forum/bricks/' + str(data['part_name']) + '/rate/', {'score': 2.9})
        self.assertEqual(response.status_code, 200)
        # comment a experience
        response = client.post(
            '/api/forum/posts/',
            {
                'experience_id': exp_id,
                'content': 'Uhhh...what you wrote is holly shit!'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        # star an experience
        client.logout()
        client.login(username='another', password='hahaha')
        response = client.post('/api/forum/experiences/' + str(exp_id) + '/vote/')
        self.assertEqual(response.status_code, 200)
        # watch a brick
        response = client.post('/api/forum/bricks/' + str(data['part_name']) + '/watch/')
        self.assertEqual(response.status_code, 200)

    def _simulate(self):
        brick = Biobrick.objects.get(part_name='BBa_B0032')
        meta = brick.ensure_meta_exists(fetch=True)
        Experience.objects.create(brick=meta, author=self.user)
        self.assertTrue(brick.watch(self.user))
        exp = Experience.objects.create(brick=meta, author=self.another_user)
        self.assertTrue(exp.vote(self.user))
        self.assertTrue(brick.watch(self.another_user))
        self.assertTrue(brick.rate(self.user, 2.3))

        return brick, meta, exp

    def test_watch_notice(self):
        brick, meta, exp = self._simulate()

        notice = Notice.objects.filter(user=self.user)[0]
        self.assertEqual(
            notice.message,
            '[[another]]((user))((another)) published a new experience'
            ' [[]]((experience))((%s)) at brick '
            '[[BBa_B0032]]((brick))((BBa_B0032)).' % exp.id
        )

    def test_vote(self):

        brick = Biobrick.objects.get(part_name='BBa_B0032')
        meta = brick.ensure_meta_exists(fetch=True)
        exp = Experience.objects.create(title='title', brick=meta, author=self.another_user)
        self.assertFalse(exp.vote(self.another_user))
        self.assertTrue(exp.vote(self.user))

        self.assertEqual(Notice.objects.count(), 1)
        self.assertEqual(
            Notice.objects.all()[0].message,
            '[[abc]]((user))((abc)) voted your experience '
            '[[title]]((experience))((%s)) at brick [[BBa_B0032]]((brick))((BBa_B0032)).'
            ' Now you have 1 vote(s) for that experience.' % exp.id
        )

    def test_only_fetching_one_user_activities(self):

        brick, meta, exp = self._simulate()
        response = self.client.get('/api/forum/activities/?user=abc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 4)

    def test_unwatch(self):

        brick, meta, exp = self._simulate()

        cnt = Activity.objects.count()

        self.assertTrue(brick.unwatch(self.user))
        self.assertEqual(Activity.objects.count(), cnt - 1)

    def test_unvote(self):

        brick, meta, exp = self._simulate()

        cnt = Activity.objects.count()
        ncnt = Notice.objects.count()

        exp.unvote(self.user)
        self.assertEqual(Activity.objects.count(), cnt - 1)
        self.assertEqual(Notice.objects.count(), ncnt - 1)

    def _make_experience(self):

        brick = Biobrick.objects.get(part_name='BBa_B0032')
        meta = brick.ensure_meta_exists(fetch=True)
        return Experience.objects.create(brick=meta, author=self.user)

    def test_make_post(self):

        exp = self._make_experience()

        Post.objects.create(content='2333', author=self.user, experience=exp)

        self.assertEqual(Activity.objects.filter(type='Comment').count(), 1)
        self.assertEqual(Notice.objects.count(), 0)

        for _ in range(3):
            Post.objects.create(content='2333', author=self.another_user, experience=exp)

        self.assertEqual(Notice.objects.count(), 1)
        notice = Notice.objects.all()[0]
        self.assertEqual(
            notice.message,
            '[[another]]((user))((another)) commented your experience'
            ' [[]]((experience))((%s)) at brick [[BBa_B0032]]((brick))((BBa_B0032)).' % exp.id
        )

    def test_delete_post(self):

        exp = self._make_experience()

        post = Post.objects.create(content='2333', author=self.another_user, experience=exp)
        post.delete()

        self.assertEqual(Activity.objects.filter(type='Comment').count(), 0)
        self.assertEqual(Notice.objects.count(), 0)

    def test_delete_experience(self):

        exp = self._make_experience()

        Post.objects.create(content='2333', author=self.another_user, experience=exp)
        exp.delete()

        self.assertEqual(Activity.objects.filter(type='Experience').count(), 0)
        self.assertEqual(Notice.objects.count(), 0)

        self.assertEqual(Post.objects.count(), 0)

    def test_fetching_specific_type_activities(self):

        brick = Biobrick.objects.get(part_name='BBa_B0032')
        meta = brick.ensure_meta_exists(fetch=True)
        Experience.objects.create(brick=meta, author=self.user)
        self.assertTrue(brick.watch(self.user))
        Experience.objects.create(brick=meta, author=self.another_user)
        self.assertTrue(brick.watch(self.another_user))
        self.assertTrue(brick.rate(self.user, 2.3))

        response = self.client.get('/api/forum/activities/?user=abc&type=Rating')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['type'], 'Rating')

        response = self.client.get('/api/forum/activities/?user=abc&type=Rating,Watch')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(
            set(x['type'] for x in response.data['results']),
            {'Rating', 'Watch'}
        )
