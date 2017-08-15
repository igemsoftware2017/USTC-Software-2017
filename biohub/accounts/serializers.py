import smtplib

from django.core import signing
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, status
from rest_framework.exceptions import Throttled

from biohub.utils.rest.serializers import bind_model,\
    ModelSerializer
from biohub.utils.url import add_params

from .mail import get_password_reset_email
from .models import User


@bind_model(User)
class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        exclude = ('password', 'followers',)
        read_only_fields = ('last_logined', 'avatar_url')


class RegisterSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user

    def validate_password(self, value):
        validate_password(value)

        return value

    class Meta:
        model = User
        fields = ('username', 'password', 'email')


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        user = self.__user = authenticate(
            username=data['username'],
            password=data['password'])

        if user is None:
            raise serializers.ValidationError(
                'Username or password is incorrect.')

        return data

    def create(self, validated_data):
        return self.__user


class ChangePasswordSerializer(serializers.Serializer):

    old = serializers.CharField(required=True)
    new1 = serializers.CharField(required=True)
    new2 = serializers.CharField(required=True)

    def validate_old(self, value):
        username = self.context['request'].user.username

        if authenticate(username=username, password=value) is None:
            raise serializers.ValidationError(
                'Old password mismatched!')

        return value

    def validate(self, data):

        new, new2 = data['new1'], data['new2']
        if new and new2 and new != new2:
            raise serializers.ValidationError(
                'New passwords mismatched!')

        validate_password(new)

        return data

    def create(self, validated_data):
        user = self.context['request'].user

        user.set_password(validated_data['new1'])
        user.save()

        return user


PASSWORD_RESET_THROTTLE = 60
PASSWORD_RESET_SIGNING_EXPIRATION = 5 * 60


class PasswordResetPerformSerializer(serializers.Serializer):

    sign = serializers.CharField(write_only=True)
    new_password = serializers.CharField(required=True)

    def validate_sign(self, value):
        try:
            self.signed_data = signing.loads(value, max_age=PASSWORD_RESET_SIGNING_EXPIRATION)
        except signing.SignatureExpired:
            raise serializers.ValidationError('Signature expired.')
        except signing.BadSignature:
            raise serializers.ValidationError('Bad signature.')

        try:
            self.user = User.objects.get(pk=self.signed_data.get('user_id', None))
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist.')

        return value

    def validate_new_password(self, value):
        validate_password(value)

        return value

    def create(self, data):
        self.user.set_password(data['new_password'])
        self.user.save()

        return 'OK'


def password_reset_cache_key(user_id):
    return 'accounts:password:reset:user:%s' % user_id


class PasswordResetRequestSerializer(serializers.Serializer):

    callback = serializers.URLField(write_only=True, required=True)
    lookup = serializers.CharField(required=True)

    @property
    def throttle_cache_key(self):
        return password_reset_cache_key(self.user.id)

    def _set_cache(self):
        cache.set(self.throttle_cache_key, 1, timeout=PASSWORD_RESET_THROTTLE)

    def _get_cache(self):
        return cache.get(self.throttle_cache_key)

    def validate_lookup(self, value):
        from django.db.models import Q

        try:
            self.user = User.objects.get(Q(username=value) | Q(email=value))
        except User.DoesNotExist:
            raise serializers.ValidationError('Should be an existed username or email.')

        return value

    def create(self, validated_data):

        if self._get_cache() is not None:
            raise Throttled()

        callback = validated_data['callback']
        signed_data = signing.dumps(dict(callback=callback, user_id=self.user.pk))
        callback = add_params(callback, sign=signed_data)

        email_message = get_password_reset_email(self.user, callback)

        try:
            email_message.send()
        except smtplib.SMTPServerDisconnected as e:
            raise serializers.ValidationError(
                'Mail sending timeout.', code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except smtplib.SMTPException as e:
            raise serializers.ValidationError(
                'Unknown SMTP error: %s.' % str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            self._set_cache()

        return 'OK'
