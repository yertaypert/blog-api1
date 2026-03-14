from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from .validators import TimezoneValidator


User = get_user_model()
logger = logging.getLogger('users')

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

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'avatar')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                _("User with this email already exists.")
            )
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        logger.debug('Created user object in serializer: %s', user.email)
        return user

    def to_representation(self, instance):
        """Return user data + token"""
        data = super().to_representation(instance)
        refresh = RefreshToken.for_user(instance)
        data['tokens'] = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        data.pop('password', None)
        return data
    

class UserPreferencesSerializer(serializers.ModelSerializer):

    timezone = serializers.CharField(
        source='preferred_timezone',
        validators=[TimezoneValidator()]
    )

    class Meta:
        model = User
        fields = ("preferred_language", "timezone")