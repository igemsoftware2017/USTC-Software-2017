from django.contrib.auth import authenticate
from rest_framework import serializers

from biohub.utils.rest.serializers import bind_model,\
    ModelSerializer

from .models import User


@bind_model(User)
class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(required=True)

    def validate(self, data):
        password, password2 = data['password'], data['password2']
        if password and password2 and password != password2:
            raise serializers.ValidationError(
                'Passwords mismatched!')

        return data

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email')


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
