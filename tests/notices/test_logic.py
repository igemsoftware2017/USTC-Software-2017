from rest_framework.test import APITestCase

from biohub.notices import tool
from biohub.accounts.models import User
from biohub.notices.models import Notice


class NoticeTestCase(APITestCase):

    def setUp(self):
        self.users = [
            User.objects.create_test_user(x)
            for x in map(lambda i: 'user_%s' % i, range(10))]

        tool.Dispatcher('a').group_send(self.users, '')
        tool.Dispatcher('b').group_send(self.users, '')


class TestQS(NoticeTestCase):

    def test_categories(self):
        self.assertSequenceEqual(Notice.objects.categories(), ['a', 'b'])

    def test_stats(self):
        Notice.objects.filter(category='a')[0].mark_read()
        self.assertSequenceEqual([
            {
                'category': 'a',
                'count': 10,
                'unread': 9,
            }, {
                'category': 'b',
                'count': 10,
                'unread': 10
            }], Notice.objects.stats())

    def test_user_stats(self):
        Notice.objects.filter(category='a').mark_read()
        self.assertSequenceEqual([
            {'user': user.id, 'unread': 1, 'count': 2}
            for user in self.users
        ], Notice.objects.users_stats(self.users))

    def test_mark_read(self):
        qs = Notice.objects.filter(category='a')
        qs.mark_read()
        self.assertSequenceEqual(qs.stats(), [{
            'category': 'a',
            'count': 10,
            'unread': 0
        }])

    def test_user(self):
        qs = Notice.objects.user_notices(self.users[0])
        self.assertEqual(len(qs), 2)

    def test_unread(self):
        self.assertTrue(all(not n.has_read for n in Notice.objects.unread()))


class TestCRUD(NoticeTestCase):

    def test_no_authentication(self):
        resp = self.client.get('/api/notices/')

        self.assertEqual(resp.status_code, 403)

    def _get(self, user, part=''):
        self.client.force_authenticate(user)
        return self.client.get('/api/notices/' + part)

    def test_list(self):
        user = self.users[0]
        resp = self._get(user)

        self.assertEqual(2, len(resp.data.get('results', ())))

    def test_filter(self):
        resp = self._get(self.users[0], '?has_read=True')

        self.assertEqual(0, len(resp.data.get('results', [1])))

    def test_retrieve(self):
        user1, user2 = self.users[:2]
        n1, n2 = [u.notices.all()[0] for u in (user1, user2)]

        resp = self._get(user1, '%d/' % n1.id)
        self.assertEqual(resp.data.get('id', ''), n1.id)

        resp = self._get(user1, '%d/' % n2.id)
        self.assertEqual(resp.status_code, 404)

    def test_mark_read(self):
        user1, user2 = self.users[:2]
        n = user2.notices.all()[0]

        self._get(user1, 'mark_all_as_read/')
        self.assertEqual(0, user1.notices.unread().count())

        self._get(user2, '%d/mark_read/' % n.id)
        n.refresh_from_db()
        self.assertTrue(n.has_read)

        resp = self._get(user2, 'stats/')
        self.assertSequenceEqual(resp.data, [{
            'category': 'a',
            'count': 1,
            'unread': 1
        }, {
            'category': 'b',
            'count': 1,
            'unread': 0
        }])

    def test_id_filter(self):
        user1 = self.users[0]
        ns = user1.notices.values_list('id', flat=True)

        resp = self._get(user1, '?ids=%s' % ','.join(map(str, ns)))
        self.assertEqual(2, len(resp.data.get('results', [])))
