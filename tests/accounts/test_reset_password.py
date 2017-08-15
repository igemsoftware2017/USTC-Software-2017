import re
from contextlib import contextmanager
from time import sleep
from urllib.parse import quote

from rest_framework.test import APITestCase

from biohub.accounts.models import User
from biohub.accounts import serializers

from django.core import mail


@contextmanager
def patch_expiration(value):
    old = serializers.PASSWORD_RESET_SIGNING_EXPIRATION
    serializers.PASSWORD_RESET_SIGNING_EXPIRATION = value

    yield

    serializers.PASSWORD_RESET_SIGNING_EXPIRATION = old


class Base(APITestCase):

    valid_callback = 'http://localhost/?a=1#2333'

    def request_url(self, callback=valid_callback, email=True):
        return '/api/users/reset_password/?callback=%s&lookup=%s' % (
            quote(callback),
            quote(self.me.email if email else self.me.username)
        )

    def setUp(self):
        self.me = User.objects.create_test_user('me')
        self.old_throttle = serializers.PASSWORD_RESET_THROTTLE
        serializers.PASSWORD_RESET_THROTTLE = 1

        if hasattr(mail, 'outbox'):
            mail.outbox.clear()

    def tearDown(self):
        serializers.PASSWORD_RESET_THROTTLE = self.old_throttle


class TestPerform(Base):

    def sign_from_mail(self):
        from biohub.utils.url import get_params
        body = mail.outbox[-1].body
        url = re.findall(r'<a href="(.*?)".*?>\1</a>', body)[0]
        return get_params(url)['sign']

    def _post(self, **payload):
        return self.client.post('/api/users/reset_password/', data=payload)

    def test_bad_signature(self):
        resp = self._post(sign='a')

        self.assertEqual(resp.status_code, 400)
        self.assertIn('Bad signature.', resp.data['sign'])

    def test_success(self):
        c = self.client
        new_password = 'a12345678'

        self.assertEqual(c.get(self.request_url()).status_code, 200)

        resp = self._post(sign=self.sign_from_mail(), new_password=new_password)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(
            self.me.pk,
            serializers.authenticate(username=self.me.username, password=new_password).pk
        )

    def test_expired(self):
        with patch_expiration(.5):
            c = self.client
            new_password = 'a12345678'

            self.assertEqual(c.get(self.request_url()).status_code, 200)

            sleep(.5)

            resp = self._post(sign=self.sign_from_mail(), new_password=new_password)
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(resp.data['sign'], ['Signature expired.'])

    def test_permission(self):
        resp = self._post()

        self.assertNotEqual(resp.status_code, 403)

    def test_user_not_exist(self):
        c = self.client
        new_password = 'a12345678'

        self.assertEqual(c.get(self.request_url()).status_code, 200)
        self.me.delete()

        resp = self._post(sign=self.sign_from_mail(), new_password=new_password)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('exist', resp.data['sign'][0])


class TestRequest(Base):

    def test_bad_callback(self):
        c = self.client

        self.assertIn(
            'callback',
            c.get('/api/users/reset_password/').data
        )

    def test_bad_lookup(self):
        self.assertIn(
            b'exist',
            self.client.get('/api/users/reset_password/?lookup=a').content
        )

    def test_username_success(self):
        c = self.client

        self.assertEqual(c.get(self.request_url(email=False)).status_code, 200)
        self.assertEqual(1, len(mail.outbox))

        m = mail.outbox[0]

        self.assertEqual(m.to, [self.me.email])
        self.assertIn('localhost', m.body)

    def test_email_success(self):
        c = self.client

        self.assertEqual(c.get(self.request_url(email=True)).status_code, 200)
        self.assertEqual(1, len(mail.outbox))

        m = mail.outbox[0]

        self.assertEqual(m.to, [self.me.email])
        self.assertIn('localhost', m.body)

    def test_throttle(self):

        c = self.client

        self.assertEqual(c.get(self.request_url()).status_code, 200)
        self.assertEqual(c.get(self.request_url()).status_code, 429)
        sleep(1)
        self.assertEqual(c.get(self.request_url()).status_code, 200)
