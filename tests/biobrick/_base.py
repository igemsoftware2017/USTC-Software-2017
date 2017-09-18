from rest_framework.test import APITestCase

from biohub.accounts.models import User


class BiobrickTest(APITestCase):

    @property
    def base_url(self):
        from django.core.urlresolvers import reverse

        return reverse('api:forum:biobrick-list')

    def _pre_setup(self, *args, **kwargs):
        super(BiobrickTest, self)._pre_setup(*args, **kwargs)

        self.me = User.objects.create_test_user('me')
        self.you = User.objects.create_test_user('you')
