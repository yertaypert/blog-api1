import logging

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model


User = get_user_model()
logger = logging.getLogger('users')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'avatar')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        logger.debug('Created user object in serializer: %s', user.email)
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        refresh = RefreshToken.for_user(instance)
        data['tokens'] = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        data.pop('password', None)
        return data


class LoggingTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get(self.username_field)
        logger.info('Login attempt for email: %s', email)
        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            logger.warning('Login failed for email: %s', email)
            raise
        except Exception:
            logger.exception('Unexpected login error for email: %s', email)
            raise

        logger.info('Login succeeded for email: %s', email)
        return data
