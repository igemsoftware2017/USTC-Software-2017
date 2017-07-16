from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.functional import cached_property

from django.utils.translation import ugettext_lazy as _

DEFAULT_AVATAR_URL = getattr(settings, 'BIOHUB_DEFAULT_AVATAR_URL', '')


class User(AbstractUser):

    description = models.TextField(_('description'), blank=True)
    avatar_url = models.URLField(_('avatar'), default=DEFAULT_AVATAR_URL)
    education = models.CharField(_('education'), blank=True, max_length=200)
    major = models.TextField(_('major'), blank=True, max_length=200)

    @cached_property
    def api_url(self):
        from django.urls import reverse

        return reverse('api:accounts:user-detail', kwargs={'pk': self.id})
