from biohub.utils.test import skip_if_no_environ
from django.test import SimpleTestCase
from django.core import mail


@skip_if_no_environ('TEST_REAL_EMAIL')
class Test(SimpleTestCase):

    def setUp(self):
        self.connection = mail.get_connection('django.core.mail.backends.smtp.EmailBackend')

    def test_send_real_mail(self):
        m = mail.EmailMessage('title', '<b>body</b>', to=['hsfzxjy@163.com'], connection=self.connection)
        m.content_subtype = 'html'
        m.send()
