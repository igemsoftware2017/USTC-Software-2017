from biohub.accounts.models import User
from rest_framework.test import APITestCase, APILiveServerTestCase


class TestLiveServer(APILiveServerTestCase):

    def setUp(self):
        self.users = []
        for i in range(5):
            self.users.append(User.objects.create_test_user('me{}'.format(i)))

    def tearDown(self):
        from biohub.biobrick.cache import _storage, _views_storage

        _storage.delete_pattern('*')
        _views_storage.delete_pattern('*')

    def test_popular(self):
        from biohub.biobrick.models import Biobrick

        self.client.get('/api/forum/bricks/BBa_B0015/?nofetch=1')

        for part in Biobrick.objects.only('part_name')[:70]:
            for user in self.users:
                self.client.force_authenticate(user)
                self.client.get('/api/forum/bricks/{}/?nofetch=1'.format(part.part_name))
        self.client.get('/api/forum/bricks/popular/')


class Test(APITestCase):

    def tearDown(self):
        from biohub.biobrick.cache import _storage, _views_storage

        _storage.delete_pattern('*')
        _views_storage.delete_pattern('*')

    def test_getter(self):
        from biohub.biobrick.cache import BrickGetter

        getter = BrickGetter()
        data = getter.get('BBa_B0015', 'BBa_B0010', 'BBa_K2042000')
        self.assertEqual(
            {'BBa_B0015', 'BBa_B0010', 'BBa_K2042000'},
            {item['part_name'] for item in data}
        )

    def test_get_related(self):

        from biohub.biobrick.cache import BrickGetter
        from biohub.biobrick.models import Biobrick

        getter = BrickGetter()
        bricks = getter.get_related_bricks('BBa_I3521')

        brick = Biobrick.objects.get(part_name='BBa_I3521')
        self.assertEqual(
            set(item['part_name'] for item in bricks),
            set('BBa_' + item['short_name'] for item in brick.ruler['sub_parts'])
        )

        data = self.client.get('/api/forum/bricks/BBa_I3521/related/').data
        self.assertEqual(
            set(item['part_name'] for item in data),
            set('BBa_' + item['short_name'] for item in brick.ruler['sub_parts'])
        )
