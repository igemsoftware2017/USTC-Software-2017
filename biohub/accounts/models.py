from django.db import models
from django.utils.functional import cached_property
from django.core.validators import MaxLengthValidator

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

from biohub.accounts.validators import UsernameValidator


class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_test_user(self, username, **extra_fields):

        if not username:
            raise ValueError('The given username must be set')

        user = self.model(username=username, email='1@2.com', **extra_fields)
        user.set_password(self.model._test_password)
        user.save(using=self._db)

        return user

    def create_user(self, username, password, email=None, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    create_superuser = create_user


class User(AbstractBaseUser):

    _test_password = '12345ab'

    username = models.CharField(
        'username',
        max_length=20,
        unique=True,
        validators=[UsernameValidator()],
        error_messages={
            'unique': ('A user with that username already exists.'),
        })
    email = models.EmailField('email address', blank=True)
    address = models.CharField(
        'address',
        max_length=200,
        blank=True,
        validators=[MaxLengthValidator(200)])
    site_url = models.URLField('personal site url', blank=True)
    description = models.TextField('personal description', blank=True)

    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following')

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'

    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        return self.username

    get_short_name = get_full_name

    objects = UserManager()

    @cached_property
    def api_url(self):
        from django.urls import reverse

        return reverse('api:accounts:user-detail', kwargs={'pk': self.id})

    def follow(self, target_user):
        """
        To follow a specific user.
        """

        if (target_user.id == self.id or
                target_user.followers.filter(pk=self.id).exists()):
            return

        target_user.followers.add(self)

    def unfollow(self, target_user):
        """
        To unfollow a specific user.
        """
        target_user.followers.remove(self)
