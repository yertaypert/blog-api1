# Python modules
import logging
from typing import Any

# Django modules
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

# Django Rest Framework modules
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

# Project modules
from .constants import USERS_LOGGER_NAME
from .validators import TimezoneValidator


User = get_user_model()
logger = logging.getLogger(USERS_LOGGER_NAME)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        error_messages={
            "required": _("Password is required."),
            "blank": _("Password cannot be empty."),
        }
    )
    password2 = serializers.CharField(
        write_only=True,
        error_messages={
            "required": _("Password confirmation is required."),
            "blank": _("Password confirmation cannot be empty."),
        }
    )
    preferred_language = serializers.CharField(required=False)
    preferred_timezone = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
            "avatar",
            "preferred_language",
            "preferred_timezone",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                _("User with this email already exists.")
            )
        return value

    def create(self, validated_data: dict[str, Any]) -> User:
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        logger.debug('Created user object in serializer: %s', user.email)
        return user

    def to_representation(self, instance: User) -> dict[str, Any]:
        data = super().to_representation(instance)
        refresh = RefreshToken.for_user(instance)
        data["tokens"] = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        data.pop('password', None)
        return data


class LoggingTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
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
    

class UserPreferencesSerializer(serializers.ModelSerializer):

    timezone = serializers.CharField(
        source='preferred_timezone',
        validators=[TimezoneValidator()]
    )

    class Meta:
        model = User
        fields = ("preferred_language", "timezone")
