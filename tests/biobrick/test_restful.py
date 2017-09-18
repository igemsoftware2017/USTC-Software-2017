from decimal import Decimal

from biohub.biobrick.models import Biobrick

from ._base import BiobrickTest


class Test(BiobrickTest):

    def setUp(self):
        self.brick = Biobrick.objects.get(part_name='BBa_E1010')

    def brick_url(self, brick=None):
        if brick is None:
            brick = self.brick

        return '{}{}/'.format(self.base_url, brick.part_name)

    def test_retrieve(self):
        self.assertFalse(self.brick.meta_exists)
        self.client.get(self.brick_url())
        self.brick.refresh_from_db()
        self.assertTrue(self.brick.meta_exists)

    def test_fields_exist(self):
        meta = self.brick.ensure_meta_exists(fetch=True)
        meta.fetch()
        self.assertTrue(bool(meta.part_type))
        self.assertGreater(meta.uses, 0)

    def test_watch(self):
        url = self.brick_url() + 'watch/'
        self.assertEqual(self.client.get(url).status_code, 403)

        self.client.force_authenticate(self.me)
        res = self.client.post(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            self.client.get(self.me.api_url + 'bricks_watching/').data['results'][0]['part_name'],
            self.brick.part_name
        )
        self.assertEqual(
            self.client.get(self.me.api_url + 'bricks_watching/').data['results'][0]['part_type'],
            self.brick.part_type
        )
        self.assertEqual(
            self.client.get(self.brick_url() + 'users_watching/').data['results'][0]['id'],
            self.me.pk
        )
        self.brick.refresh_from_db()
        self.assertEqual(self.brick.watches, 1)

    def test_unwatch(self):

        self.test_watch()

        self.assertEqual(
            self.client.post(self.brick_url() + 'unwatch/').status_code,
            200
        )
        self.assertEqual(
            self.client.get(self.brick_url() + 'users_watching/').data['count'],
            0
        )
        self.assertEqual(
            self.client.get(self.me.api_url + 'bricks_watching/').data['count'],
            0
        )
        self.brick.refresh_from_db()
        self.assertEqual(self.brick.watches, 0)

    def test_star(self):
        url = self.brick_url() + 'star/'
        self.assertEqual(self.client.get(url).status_code, 403)

        self.client.force_authenticate(self.me)
        res = self.client.post(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            self.client.get(self.me.api_url + 'bricks_starred/?detail').data['results'][0]['part_name'],
            self.brick.part_name
        )
        self.assertEqual(
            self.client.get(self.brick_url() + 'users_starred/').data['results'][0]['id'],
            self.me.pk
        )
        self.brick.refresh_from_db()
        self.assertEqual(self.brick.stars, 1)

    def test_unstar(self):
        self.test_star()

        self.assertEqual(self.client.post(self.brick_url() + 'unstar/').status_code, 200)
        self.assertEqual(
            self.client.get(self.brick_url() + 'users_starred/').data['count'],
            0
        )
        self.assertEqual(
            self.client.get(self.me.api_url + 'bricks_starred/').data['count'],
            0
        )
        self.brick.refresh_from_db()
        self.assertEqual(self.brick.stars, 0)

    def test_rate(self):

        ae = self.assertEqual
        code = lambda res, c: ae(res.status_code, c)  # noqa
        success = lambda res: code(res, 200)  # noqa

        def rate(user, score):
            self.client.force_authenticate(user)

            return self.client.post(self.brick_url() + 'rate/', {'score': score})

        code(rate(self.me, -0.1), 400)
        code(rate(self.me, 5.1), 400)
        success(rate(self.me, 2.5))
        code(rate(self.me, 2.5), 400)
        success(rate(self.you, 5))

        self.brick.refresh_from_db()
        ae(self.brick.rate_score, Decimal('3.8'))
        ae(self.brick.rates, 2)
