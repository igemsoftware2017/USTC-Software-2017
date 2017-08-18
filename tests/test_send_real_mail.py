import os

from unittest import skipIf
from django.test import SimpleTestCase
from django.core import mail


@skipIf(not os.environ.get('TEST_REAL_EMAIL', 0), '')
class Test(SimpleTestCase):

    def setUp(self):
        self.connection = mail.get_connection('django.core.mail.backends.smtp.EmailBackend')

    def test_send_real_mail(self):
        m = mail.EmailMessage('title', 'body', to=['hsfzxjy@163.com'], connection=self.connection)
        m.send()
